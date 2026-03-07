"""FastAPI 应用入口"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.dependencies.database import engine
from app.models import Base
from app.services.monitor_service import get_monitor_service
from app.utils.logger import setup_logger

# 配置日志
logger = setup_logger(__name__)

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="SkillHub - 社区驱动的开放技能平台 API",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

import time
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """全局 HTTP 访问日志记录与耗时统计"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # 构建结构化日志信息
    log_dict = {
        "client": request.client.host if request.client else "unknown",
        "method": request.method,
        "url": request.url.path,
        "status_code": response.status_code,
        "process_time_ms": round(process_time * 1000, 2)
    }
    
    # 对于正常的静态文件或健康检查不频繁刷屏，其余打 INFO
    if request.url.path in ["/health", "/api/health"]:
        logger.debug(f"{log_dict['method']} {log_dict['url']} - {log_dict['status_code']} - {log_dict['process_time_ms']}ms")
    else:
        logger.info(f"{log_dict['method']} {log_dict['url']} - {log_dict['status_code']} - {log_dict['process_time_ms']}ms - IP: {log_dict['client']}")
        
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """自定义验证错误处理，返回更友好的错误信息"""
    errors = []
    for err in exc.errors():
        field = ".".join([str(x) for x in err["loc"] if x != "body"])
        msg = err["msg"]
        
        field_name_map = {
            "username": "用户名",
            "email": "邮箱",
            "password": "密码",
            "old_password": "旧密码",
            "new_password": "新密码"
        }
        field = field_name_map.get(field, field)
        
        if "string_too_short" in err["type"]:
            min_length = err["ctx"].get("min_length", 0)
            msg = f"{field}长度至少需要{min_length}个字符"
        elif "string_too_long" in err["type"]:
            max_length = err["ctx"].get("max_length", 0)
            msg = f"{field}长度不能超过{max_length}个字符"
        elif "value_error.email" in err["type"]:
            msg = f"{field}格式不正确"
        
        errors.append(msg)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "; ".join(errors)}
    )


logger.info("SkillHub API 启动成功")


@app.get("/")
async def root():
    return {
        "message": "Welcome to SkillHub API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    monitor = get_monitor_service()
    return monitor.get_health_status()

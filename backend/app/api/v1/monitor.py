"""监控相关 API"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.monitor_service import get_monitor_service
from app.services.notify_service import get_notification_service
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    app_name: str
    timestamp: float
    system: Dict[str, Any]
    database: Dict[str, Any]
    redis: Optional[Dict[str, Any]] = None


class NotificationTestRequest(BaseModel):
    """通知测试请求"""

    title: str = "测试通知"
    message: str = "这是一条测试通知消息"
    level: str = "info"


@router.get("/health", summary="健康检查")
async def health_check():
    """完整健康检查端点"""
    monitor = get_monitor_service()
    try:
        return monitor.get_health_status()
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")


@router.get("/health/live", summary="存活检查")
async def liveness_check():
    """存活检查 - 用于 Kubernetes liveness probe"""
    return {"status": "alive"}


@router.get("/health/ready", summary="就绪检查")
async def readiness_check():
    """就绪检查 - 用于 Kubernetes readiness probe"""
    monitor = get_monitor_service()
    db_status = monitor.check_database()

    if db_status["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="服务未就绪")


@router.get("/metrics", summary="系统指标")
async def get_metrics():
    """获取系统指标"""
    monitor = get_monitor_service()
    try:
        return monitor.get_system_info()
    except Exception as e:
        logger.error(f"获取系统指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取系统指标失败")


@router.post("/notify/test", summary="测试通知")
async def test_notification(request: NotificationTestRequest):
    """发送测试通知"""
    notify = get_notification_service()
    try:
        success = await notify.send_info(request.title, request.message)
        return {"success": success, "message": "测试通知已发送" if success else "通知服务未启用或发送失败"}
    except Exception as e:
        logger.error(f"测试通知发送失败: {str(e)}")
        raise HTTPException(status_code=500, detail="测试通知发送失败")

"""
安全扫描相关 API
"""
import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.scan import (
    ScanCodeRequest,
    ScanDirectoryRequest,
    ScanDirectoryResult,
    ScanHealthResponse,
    ScanResult,
)
from app.services.scan_service import ScanService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=ScanHealthResponse)
def get_health():
    """健康检查"""
    logger.debug("扫描服务健康检查")
    return ScanHealthResponse(status="ok", version="1.0.0")


@router.post("/code", response_model=ScanResult)
def scan_code(request: ScanCodeRequest):
    """
    扫描代码安全问题

    可以通过两种方式扫描：
    1. 提供 code_content：直接扫描代码字符串
    2. 提供 file_path：扫描指定文件
    """
    logger.info(f"扫描代码请求: skill_id={request.skill_id}")

    try:
        result = ScanService.scan_skill_code(
            skill_id=request.skill_id,
            code_content=request.code_content,
            file_path=request.file_path,
        )

        # 转换为响应模型
        return ScanResult(
            success=result["success"],
            message=result["message"],
            skill_id=result.get("skill_id"),
            issues=result.get("issues", []),
            files_scanned=result.get("files_scanned", 0),
            total_issues=result.get("total_issues", 0),
            summary=result.get("summary", {}),
        )

    except Exception as e:
        logger.error(f"扫描代码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"扫描失败: {str(e)}"
        )


@router.post("/directory", response_model=ScanDirectoryResult)
def scan_directory(request: ScanDirectoryRequest):
    """
    扫描目录安全问题
    """
    logger.info(
        f"扫描目录请求: directory_path={request.directory_path}, skill_id={request.skill_id}"
    )

    try:
        issues, files_scanned, total_issues = ScanService.scan_directory(
            request.directory_path
        )

        # 生成摘要
        summary_dict = ScanService._generate_summary(issues)

        return ScanDirectoryResult(
            success=True,
            message="扫描完成",
            skill_id=request.skill_id,
            issues=[issue.to_dict() for issue in issues],
            files_scanned=files_scanned,
            total_issues=total_issues,
            summary=summary_dict,
        )

    except Exception as e:
        logger.error(f"扫描目录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"扫描失败: {str(e)}"
        )

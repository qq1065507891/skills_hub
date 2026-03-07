"""
技能发布相关 API
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.skill import PublicationResponse
from app.services.skill_service import SkillService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_skill_package(
    skill_id: int = Query(..., description="技能ID"),
    file: UploadFile = File(..., description="技能包文件"),
    db: Session = Depends(get_db),
):
    """上传技能包文件"""
    logger.info(f"上传技能包请求: skill_id={skill_id}, filename={file.filename}, content_type={file.content_type}")

    service = SkillService(db)
    try:
        file_path = service.save_skill_package(skill_id, file.file, file.filename, file.content_type)
        # 验证技能包
        service.validate_skill_package(file_path)
        return {
            "success": True,
            "message": "技能包上传成功",
            "data": {"file_path": file_path, "filename": file.filename},
        }
    except ValueError as e:
        logger.warning(f"上传技能包失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/submit/{skill_id}",
    response_model=PublicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_publication(
    skill_id: int,
    notes: Optional[str] = Query(None, description="发布说明"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """提交技能发布"""
    logger.info(f"提交发布请求: skill_id={skill_id}, user_id={current_user.id}")

    service = SkillService(db)
    try:
        publication = service.create_publication(skill_id, current_user.id, notes)
        return publication
    except ValueError as e:
        logger.warning(f"提交发布失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/skill/{skill_id}", response_model=List[PublicationResponse])
async def get_skill_publications(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """获取技能的发布记录"""
    logger.debug(f"获取技能发布记录: skill_id={skill_id}")

    service = SkillService(db)
    return service.get_publications_by_skill(skill_id)


@router.get("/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
):
    """获取单个发布记录"""
    logger.debug(f"获取发布记录: publication_id={publication_id}")

    service = SkillService(db)
    publication = service.get_publication(publication_id)
    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found",
        )
    return publication


@router.patch("/{publication_id}/status", response_model=PublicationResponse)
async def update_publication_status(
    publication_id: int,
    status: str = Query(..., description="发布状态"),
    notes: Optional[str] = Query(None, description="备注"),
    db: Session = Depends(get_db),
):
    """更新发布状态（审核）"""
    logger.info(f"更新发布状态: publication_id={publication_id}, status={status}")

    service = SkillService(db)
    try:
        publication = service.update_publication_status(publication_id, status, notes)
        if publication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publication not found",
            )
        return publication
    except ValueError as e:
        logger.warning(f"更新发布状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

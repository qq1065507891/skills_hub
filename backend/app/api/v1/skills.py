"""
技能相关 API
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.skill import (
    ReviewCreate,
    ReviewResponse,
    SkillCreate,
    SkillListResponse,
    SkillResponse,
    SkillUpdate,
)
from app.services.skill_service import SkillService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=SkillListResponse)
def get_skills(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    category: Optional[str] = Query(None, description="分类过滤"),
    author_id: Optional[int] = Query(None, description="作者ID过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
):
    """获取技能列表"""
    logger.debug(f"获取技能列表: skip={skip}, limit={limit}, category={category}")
    service = SkillService(db)
    skills, total = service.get_skills(
        skip=skip, limit=limit, category=category, author_id=author_id, search=search
    )
    return SkillListResponse(total=total, items=skills)


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """获取单个技能"""
    logger.debug(f"获取技能: skill_id={skill_id}")
    service = SkillService(db)
    skill = service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return skill


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill: SkillCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建技能"""
    logger.info(f"创建技能请求：name={skill.name}, user_id={current_user.id}")
    service = SkillService(db)
    try:
        db_skill = service.create_skill(skill, current_user.id)
        return db_skill
    except ValueError as e:
        logger.warning(f"创建技能失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新技能(只能更新自己的技能)"""
    logger.info(f"更新技能请求: skill_id={skill_id}, user_id={current_user.id}")
    service = SkillService(db)
    
    # 检查技能是否存在
    existing_skill = service.get_skill(skill_id)
    if existing_skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    
    # 检查权限: 只有作者才能更新
    if existing_skill.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能更新自己创建的技能",
        )
    
    try:
        db_skill = service.update_skill(skill_id, skill_update)
        return db_skill
    except ValueError as e:
        logger.warning(f"更新技能失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除技能(只能删除自己的技能)"""
    logger.info(f"删除技能请求: skill_id={skill_id}, user_id={current_user.id}")
    service = SkillService(db)
    
    # 检查技能是否存在
    existing_skill = service.get_skill(skill_id)
    if existing_skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    
    # 检查权限: 只有作者才能删除
    if existing_skill.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己创建的技能",
        )
    
    success = service.delete_skill(skill_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return None


@router.get("/{skill_id}/versions", response_model=List[SkillResponse])
def get_skill_versions(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """获取技能的历史版本列表"""
    logger.debug(f"获取技能历史版本: skill_id={skill_id}")
    service = SkillService(db)
    
    # 检查技能是否存在
    existing_skill = service.get_skill(skill_id)
    if existing_skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    
    versions = service.get_skill_versions(skill_id)
    return versions


@router.get("/{skill_id}/versions/{version_id}", response_model=SkillResponse)
def get_skill_version(
    skill_id: int,
    version_id: int,
    db: Session = Depends(get_db),
):
    """获取单个历史版本详情"""
    logger.debug(f"获取历史版本详情: skill_id={skill_id}, version_id={version_id}")
    service = SkillService(db)
    
    # 检查技能是否存在
    existing_skill = service.get_skill(skill_id)
    if existing_skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    
    version = service.get_skill_version(version_id)
    if version is None or version.skill_id != skill_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )
    
    return version


@router.post("/{skill_id}/versions/{version_id}/download", response_model=SkillResponse)
def increment_version_download(
    skill_id: int,
    version_id: int,
    db: Session = Depends(get_db),
):
    """增加历史版本下载计数"""
    logger.debug(f"增加历史版本下载计数: skill_id={skill_id}, version_id={version_id}")
    service = SkillService(db)
    
    # 检查技能是否存在
    existing_skill = service.get_skill(skill_id)
    if existing_skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    
    version = service.get_skill_version(version_id)
    if version is None or version.skill_id != skill_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )
    
    version = service.increment_version_download_count(version_id)
    return version


@router.post("/{skill_id}/download", response_model=SkillResponse)
def increment_download(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """增加下载计数"""
    logger.debug(f"增加下载计数: skill_id={skill_id}")
    service = SkillService(db)
    skill = service.increment_download_count(skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return skill


# ========== 评价相关 API ==========


@router.get("/{skill_id}/reviews", response_model=List[ReviewResponse])
def get_reviews(
    skill_id: int,
    db: Session = Depends(get_db),
):
    """获取技能的评价列表"""
    logger.debug(f"获取评价列表: skill_id={skill_id}")
    service = SkillService(db)
    return service.get_reviews(skill_id)


@router.post(
    "/{skill_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    skill_id: int,
    review: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建评价"""
    logger.info(f"创建评价请求: skill_id={skill_id}, user_id={current_user.id}")
    service = SkillService(db)
    try:
        db_review = service.create_review(skill_id, current_user.id, review)
        return db_review
    except ValueError as e:
        logger.warning(f"创建评价失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

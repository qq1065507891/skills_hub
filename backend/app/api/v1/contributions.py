"""
贡献度相关 API
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.contribution import (
    ContributionLogListResponse,
    ContributionLogResponse,
    ContributionRankingResponse,
    UserContributionSummary,
)
from app.services.contribution_service import ContributionService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/user/{user_id}/logs", response_model=ContributionLogListResponse)
def get_user_contributions(
    user_id: int,
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
):
    """获取用户的贡献度记录列表"""
    logger.debug(f"获取用户贡献度记录: user_id={user_id}, skip={skip}, limit={limit}")
    service = ContributionService(db)
    logs, total = service.get_user_contributions(
        user_id=user_id, skip=skip, limit=limit
    )
    return ContributionLogListResponse(total=total, items=logs)


@router.get("/user/{user_id}/summary", response_model=UserContributionSummary)
def get_user_contribution_summary(
    user_id: int,
    include_rank: bool = Query(True, description="是否包含排名"),
    db: Session = Depends(get_db),
):
    """获取用户贡献度摘要"""
    logger.debug(f"获取用户贡献度摘要: user_id={user_id}")
    service = ContributionService(db)
    summary = service.get_user_summary(user_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # 可选地获取排名
    if include_rank:
        summary["rank"] = service.get_user_rank(user_id)
    return UserContributionSummary(**summary)


@router.get("/my/summary", response_model=UserContributionSummary)
def get_my_contribution_summary(
    include_rank: bool = Query(True, description="是否包含排名"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户贡献度摘要"""
    logger.debug(f"获取当前用户贡献度摘要: user_id={current_user.id}")
    service = ContributionService(db)
    summary = service.get_user_summary(current_user.id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if include_rank:
        summary["rank"] = service.get_user_rank(current_user.id)
    return UserContributionSummary(**summary)


@router.get("/my/logs", response_model=ContributionLogListResponse)
def get_my_contributions(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的贡献度记录列表"""
    logger.debug(f"获取当前用户贡献度记录: user_id={current_user.id}, skip={skip}, limit={limit}")
    service = ContributionService(db)
    logs, total = service.get_user_contributions(
        user_id=current_user.id, skip=skip, limit=limit
    )
    return ContributionLogListResponse(total=total, items=logs)


@router.get("/ranking", response_model=ContributionRankingResponse)
def get_contribution_ranking(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
):
    """获取贡献度排行榜"""
    logger.debug(f"获取贡献度排行榜: skip={skip}, limit={limit}")
    service = ContributionService(db)
    ranking, total = service.get_ranking(skip=skip, limit=limit)
    return ContributionRankingResponse(total=total, items=ranking)


@router.get("/logs/{contribution_id}", response_model=ContributionLogResponse)
def get_contribution_log(
    contribution_id: int,
    db: Session = Depends(get_db),
):
    """获取单个贡献度记录"""
    logger.debug(f"获取贡献度记录: contribution_id={contribution_id}")
    service = ContributionService(db)
    log = service.get_contribution_by_id(contribution_id)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contribution log not found",
        )
    return log

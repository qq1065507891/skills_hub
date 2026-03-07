"""
评价相关 API
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.review_service import ReviewService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/skill/{skill_id}", response_model=ReviewListResponse)
def get_reviews_by_skill(
    skill_id: int,
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
):
    """获取技能的评价列表"""
    logger.debug(f"获取技能评价列表: skill_id={skill_id}, skip={skip}, limit={limit}")
    service = ReviewService(db)
    reviews, total = service.get_reviews_by_skill(
        skill_id=skill_id, skip=skip, limit=limit
    )
    reviews_with_user = service.get_reviews_with_user_info(reviews)
    return ReviewListResponse(total=total, items=reviews_with_user)


@router.get("/user/{user_id}", response_model=ReviewListResponse)
def get_reviews_by_user(
    user_id: int,
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
):
    """获取用户的评价列表"""
    logger.debug(f"获取用户评价列表: user_id={user_id}, skip={skip}, limit={limit}")
    service = ReviewService(db)
    reviews, total = service.get_reviews_by_user(
        user_id=user_id, skip=skip, limit=limit
    )
    reviews_with_user = service.get_reviews_with_user_info(reviews)
    return ReviewListResponse(total=total, items=reviews_with_user)


@router.get("/my/skill/{skill_id}", response_model=Optional[ReviewResponse])
def get_my_review_for_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户对技能的评价"""
    logger.debug(f"获取当前用户对技能的评价: user_id={current_user.id}, skill_id={skill_id}")
    service = ReviewService(db)
    review = service.get_user_review_for_skill(current_user.id, skill_id)
    return review


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    """获取单个评价"""
    logger.debug(f"获取评价: review_id={review_id}")
    service = ReviewService(db)
    review = service.get_review(review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    return review


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建评价"""
    logger.info(f"创建评价请求: user_id={current_user.id}, skill_id={review.skill_id}")
    service = ReviewService(db)
    try:
        db_review = service.create_review(current_user.id, review)
        return db_review
    except ValueError as e:
        logger.warning(f"创建评价失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新评价"""
    logger.info(f"更新评价请求: review_id={review_id}")
    service = ReviewService(db)
    try:
        db_review = service.update_review(review_id, current_user.id, review_update)
        if db_review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return db_review
    except ValueError as e:
        logger.warning(f"更新评价失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除评价"""
    logger.info(f"删除评价请求: review_id={review_id}")
    service = ReviewService(db)
    try:
        success = service.delete_review(review_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return None
    except ValueError as e:
        logger.warning(f"删除评价失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

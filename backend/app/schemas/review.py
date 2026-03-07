"""评价相关 Pydantic 模型"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    """评价基础模型"""

    skill_id: int = Field(..., description="技能ID")
    user_id: int = Field(..., description="用户ID")
    rating: int = Field(..., ge=1, le=5, description="评分（1-5星）")
    comment: Optional[str] = Field(None, description="评价内容")


class ReviewCreate(BaseModel):
    """创建评价的请求模型"""

    skill_id: int = Field(..., description="技能ID")
    rating: int = Field(..., ge=1, le=5, description="评分（1-5星）")
    comment: Optional[str] = Field(None, description="评价内容")


class ReviewUpdate(BaseModel):
    """更新评价的请求模型"""

    rating: Optional[int] = Field(None, ge=1, le=5, description="评分（1-5星）")
    comment: Optional[str] = Field(None, description="评价内容")


class ReviewResponse(ReviewBase):
    """评价响应模型"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewWithUserResponse(BaseModel):
    """包含用户信息的评价响应模型"""

    id: int
    skill_id: int
    user_id: int
    username: str
    avatar_url: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """评价列表响应模型"""

    total: int
    items: List[ReviewWithUserResponse]

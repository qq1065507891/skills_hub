"""贡献度相关 Pydantic 模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.contribution import ActionType


class ContributionLogBase(BaseModel):
    """贡献度记录基础模型"""

    user_id: int
    action_type: ActionType
    points: int = Field(..., ge=0, description="贡献点数")
    description: Optional[str] = Field(None, max_length=500)
    related_id: Optional[int] = None


class ContributionLogCreate(ContributionLogBase):
    """创建贡献度记录"""

    pass


class ContributionLogResponse(ContributionLogBase):
    """贡献度记录响应"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ContributionLogListResponse(BaseModel):
    """贡献度记录列表响应"""

    total: int
    items: list[ContributionLogResponse]


class UserContributionSummary(BaseModel):
    """用户贡献度摘要"""

    user_id: int
    total_points: int
    total_actions: int
    create_skill_count: int
    update_skill_count: int
    write_review_count: int
    report_issue_count: int
    fix_issue_count: int
    documentation_count: int
    other_count: int
    rank: Optional[int] = None  # 排名（可选）


class ContributionRankingItem(BaseModel):
    """贡献度排名项"""

    user_id: int
    username: str
    avatar_url: Optional[str] = None
    total_points: int
    rank: int


class ContributionRankingResponse(BaseModel):
    """贡献度排名响应"""

    total: int
    items: list[ContributionRankingItem]

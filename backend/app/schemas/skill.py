"""技能相关 Pydantic 模型"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="技能名称")
    slug_name: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$", description="英文名称(用于安装命令,只能包含小写字母、数字和连字符)")
    description: Optional[str] = Field(None, description="技能描述")
    version: str = Field(
        default="1.0.0", min_length=1, max_length=50, description="版本号"
    )
    license: Optional[str] = Field("MIT", max_length=100, description="许可证类型")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    tags: Optional[str] = Field(None, max_length=1000, description="标签（逗号分隔）")
    author_id: Optional[int] = Field(None, description="作者 ID（从认证用户自动获取）")


class SkillCreate(SkillBase):
    """创建技能的请求模型"""

    pass


class SkillUpdate(BaseModel):
    """更新技能的请求模型"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="技能名称")
    slug_name: Optional[str] = Field(None, min_length=1, max_length=255, pattern="^[a-z0-9-]+$", description="英文名称")
    description: Optional[str] = Field(None, description="技能描述")
    version: Optional[str] = Field(None, min_length=1, max_length=50, description="版本号")
    license: Optional[str] = Field(None, max_length=100, description="许可证类型")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    tags: Optional[str] = Field(None, max_length=1000, description="标签（逗号分隔）")


class SkillResponse(SkillBase):
    """技能响应模型"""

    id: int
    download_count: int = 0
    rating: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillListResponse(BaseModel):
    """技能列表响应模型"""

    total: int
    items: List[SkillResponse]


class SearchResponse(BaseModel):
    """搜索响应模型"""

    items: List[SkillResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoriesResponse(BaseModel):
    """分类列表响应模型"""

    categories: List[str]


class TagsResponse(BaseModel):
    """标签列表响应模型"""

    tags: List[str]


# ========== 评价相关模型 ==========


class ReviewBase(BaseModel):
    """评价基础模型"""

    rating: int = Field(..., ge=1, le=5, description="评分（1-5星）")
    comment: Optional[str] = Field(None, description="评论内容")


class ReviewCreate(ReviewBase):
    """创建评价的请求模型"""

    pass


class ReviewResponse(ReviewBase):
    """评价响应模型"""

    id: int
    skill_id: int
    user_id: int
    created_at: datetime
    user: Optional[dict] = None  # 可选的用户信息

    class Config:
        from_attributes = True


# ========== 发布相关模型 ==========


class PublicationBase(BaseModel):
    """发布基础模型"""

    status: str = Field(..., max_length=50, description="发布状态")
    notes: Optional[str] = Field(None, description="发布说明")


class PublicationCreate(PublicationBase):
    """创建发布的请求模型"""

    skill_id: int = Field(..., description="技能ID")


class PublicationUpdate(BaseModel):
    """更新发布的请求模型"""

    status: Optional[str] = Field(None, max_length=50, description="发布状态")
    notes: Optional[str] = Field(None, description="发布说明")


class PublicationResponse(PublicationBase):
    """发布响应模型"""

    id: int
    skill_id: int
    published_by: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

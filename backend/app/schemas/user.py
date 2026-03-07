"""用户相关 Pydantic 模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    github_id: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class UserRegister(BaseModel):
    """用户注册"""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """用户登录"""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)


class Token(BaseModel):
    """JWT Token 响应"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据"""

    username: Optional[str] = None


class UserCreate(UserBase):
    """创建用户（内部使用）"""

    hashed_password: str


class UserUpdate(BaseModel):
    """更新用户"""

    username: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class UserUpdatePassword(BaseModel):
    """更新密码"""

    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class UserResponse(UserBase):
    id: int
    contribution_points: int = 0
    role: UserRole = UserRole.USER
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

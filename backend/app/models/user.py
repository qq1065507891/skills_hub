"""用户数据模型"""
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from . import Base


class UserRole(str, Enum):
    """用户角色枚举"""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    github_id = Column(String(100), unique=True, nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    contribution_points = Column(Integer, nullable=False, default=0)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    skills = relationship(
        "Skill", back_populates="author", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )
    contribution_logs = relationship(
        "ContributionLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"&lt;User(id={self.id}, username='{self.username}', role='{self.role}')&gt;"

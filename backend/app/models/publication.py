"""技能发布数据模型"""
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base


class PublicationStatus(str, Enum):
    """发布状态枚举"""

    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Publication(Base):
    """技能发布模型"""

    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    published_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        String(50), nullable=False, default=PublicationStatus.DRAFT, index=True
    )
    notes = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    skill = relationship("Skill")
    publisher = relationship("User", foreign_keys=[published_by])

    def __repr__(self):
        return f"<Publication(id={self.id}, skill_id={self.skill_id}, status='{self.status}')>"

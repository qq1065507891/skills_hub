"""技能数据模型"""
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base


class Skill(Base):
    """技能模型"""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug_name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False, default="1.0.0")
    license = Column(String(100), nullable=True, default="MIT")
    category = Column(String(100), nullable=True, index=True)
    tags = Column(String(1000), nullable=True)
    download_count = Column(Integer, nullable=False, default=0)
    rating = Column(Float, nullable=False, default=0.0)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    author = relationship("User", back_populates="skills")
    reviews = relationship(
        "Review", back_populates="skill", cascade="all, delete-orphan"
    )
    versions = relationship(
        "SkillVersion", back_populates="skill", cascade="all, delete-orphan", order_by="desc(SkillVersion.created_at)"
    )

    def __repr__(self):
        return (
            f"<Skill(id={self.id}, name='{self.name}', version='{self.version}')>"
        )

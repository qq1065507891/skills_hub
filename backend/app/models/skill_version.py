"""技能历史版本数据模型"""
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base


class SkillVersion(Base):
    """技能历史版本模型 - 存储技能的每个历史版本"""

    __tablename__ = "skill_versions"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False)
    license = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(String(1000), nullable=True)
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # 关联关系
    skill = relationship("Skill", back_populates="versions")
    author = relationship("User")

    def __repr__(self):
        return f"<SkillVersion(id={self.id}, skill_id={self.skill_id}, version='{self.version}')>"

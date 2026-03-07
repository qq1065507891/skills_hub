"""评价数据模型"""
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from . import Base


class Review(Base):
    """评价模型"""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    skill = relationship("Skill", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"&lt;Review(id={self.id}, skill_id={self.skill_id}, user_id={self.user_id}, rating={self.rating})&gt;"

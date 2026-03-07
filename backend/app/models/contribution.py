"""贡献度记录数据模型"""
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base


class ActionType(str, Enum):
    """操作类型枚举"""

    CREATE_SKILL = "create_skill"
    UPDATE_SKILL = "update_skill"
    WRITE_REVIEW = "write_review"
    REPORT_ISSUE = "report_issue"
    FIX_ISSUE = "fix_issue"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class ContributionLog(Base):
    """贡献度记录模型"""

    __tablename__ = "contribution_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    points = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    related_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    user = relationship("User", back_populates="contribution_logs")

    def __repr__(self):
        return f"&lt;ContributionLog(id={self.id}, user_id={self.user_id}, action_type='{self.action_type}', points={self.points})&gt;"

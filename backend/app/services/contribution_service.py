"""贡献度服务"""
import logging
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.contribution import ActionType, ContributionLog
from app.models.user import User

logger = logging.getLogger(__name__)


class ContributionService:
    """贡献度服务类"""

    # 操作类型对应的积分配置
    POINTS_CONFIG = {
        ActionType.CREATE_SKILL: 50,
        ActionType.UPDATE_SKILL: 10,
        ActionType.WRITE_REVIEW: 20,
        ActionType.REPORT_ISSUE: 15,
        ActionType.FIX_ISSUE: 30,
        ActionType.DOCUMENTATION: 25,
        ActionType.OTHER: 5,
    }

    def __init__(self, db: Session):
        self.db = db

    def log_contribution(
        self,
        user_id: int,
        action_type: ActionType,
        description: Optional[str] = None,
        related_id: Optional[int] = None,
        custom_points: Optional[int] = None,
    ):
        """
        记录贡献度

        Args:
            user_id: 用户ID
            action_type: 操作类型
            description: 描述
            related_id: 关联ID（如技能ID、评价ID等）
            custom_points: 自定义积分（如果不提供则使用默认配置）

        Returns:
            创建的贡献度记录
        """
        points = (
            custom_points
            if custom_points is not None
            else self.POINTS_CONFIG.get(action_type, 0)
        )

        logger.info(
            "记录贡献度: user_id=%s, action_type=%s, points=%s, related_id=%s",
            user_id,
            action_type,
            points,
            related_id,
        )

        # 创建贡献度记录
        contribution_log = ContributionLog(
            user_id=user_id,
            action_type=action_type,
            points=points,
            description=description,
            related_id=related_id,
        )
        self.db.add(contribution_log)

        # 更新用户总贡献度
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.contribution_points += points

        self.db.commit()
        self.db.refresh(contribution_log)

        return contribution_log

    def get_user_contributions(self, user_id: int, skip: int = 0, limit: int = 100):
        """
        获取用户的贡献度记录列表

        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (贡献度记录列表, 总数)
        """
        logger.debug("获取用户贡献度记录: user_id=%s, skip=%s, limit=%s", user_id, skip, limit)

        query = self.db.query(ContributionLog).filter(
            ContributionLog.user_id == user_id
        )
        total = query.count()
        logs = (
            query.order_by(ContributionLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return logs, total

    def get_user_summary(self, user_id: int):
        """
        获取用户贡献度摘要

        Args:
            user_id: 用户ID

        Returns:
            用户贡献度摘要
        """
        logger.debug("获取用户贡献度摘要: user_id=%s", user_id)

        # 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 获取各类型操作数量
        action_counts = (
            self.db.query(ContributionLog.action_type, func.count(ContributionLog.id))
            .filter(ContributionLog.user_id == user_id)
            .group_by(ContributionLog.action_type)
            .all()
        )

        count_map = {action: count for action, count in action_counts}

        # 计算总操作数
        total_actions = sum(count_map.values())

        return {
            "user_id": user_id,
            "total_points": user.contribution_points,
            "total_actions": total_actions,
            "create_skill_count": count_map.get(ActionType.CREATE_SKILL, 0),
            "update_skill_count": count_map.get(ActionType.UPDATE_SKILL, 0),
            "write_review_count": count_map.get(ActionType.WRITE_REVIEW, 0),
            "report_issue_count": count_map.get(ActionType.REPORT_ISSUE, 0),
            "fix_issue_count": count_map.get(ActionType.FIX_ISSUE, 0),
            "documentation_count": count_map.get(ActionType.DOCUMENTATION, 0),
            "other_count": count_map.get(ActionType.OTHER, 0),
            "rank": None,
        }

    def get_ranking(self, skip: int = 0, limit: int = 100):
        """
        获取贡献度排行榜

        Args:
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (排行榜项列表, 总数)
        """
        logger.debug("获取贡献度排行榜: skip=%s, limit=%s", skip, limit)

        # 查询用户按贡献度排序
        query = self.db.query(User).order_by(desc(User.contribution_points))
        total = query.count()
        users = query.offset(skip).limit(limit).all()

        # 构建排行榜数据
        ranking_items = []
        for idx, user in enumerate(users, start=skip + 1):
            ranking_items.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "avatar_url": user.avatar_url,
                    "total_points": user.contribution_points,
                    "rank": idx,
                }
            )

        return ranking_items, total

    def get_user_rank(self, user_id: int):
        """
        获取用户排名

        Args:
            user_id: 用户ID

        Returns:
            排名（从1开始），如果用户不存在返回None
        """
        logger.debug("获取用户排名: user_id=%s", user_id)

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 计算比当前用户积分高的用户数量 + 1
        rank = (
            self.db.query(func.count(User.id))
            .filter(User.contribution_points > user.contribution_points)
            .scalar()
            + 1
        )

        return rank

    def get_contribution_by_id(self, contribution_id: int):
        """
        根据ID获取贡献度记录

        Args:
            contribution_id: 贡献度记录ID

        Returns:
            贡献度记录
        """
        return (
            self.db.query(ContributionLog)
            .filter(ContributionLog.id == contribution_id)
            .first()
        )

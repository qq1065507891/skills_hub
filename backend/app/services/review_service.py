"""评价服务"""
import logging

from sqlalchemy import func

from app.models.contribution import ActionType
from app.models.review import Review
from app.models.skill import Skill
from app.models.user import User
from app.services.contribution_service import ContributionService

logger = logging.getLogger(__name__)


class ReviewService:
    """评价服务类"""

    def __init__(self, db):
        self.db = db

    def get_review(self, review_id):
        """获取单个评价"""
        logger.debug("获取评价: review_id=%s", review_id)
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_reviews_by_skill(self, skill_id, skip=0, limit=100):
        """获取技能的评价列表"""
        logger.debug("获取技能评价列表: skill_id=%s, skip=%s, limit=%s", skill_id, skip, limit)

        query = self.db.query(Review).filter(Review.skill_id == skill_id)
        total = query.count()
        reviews = (
            query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
        )

        logger.debug("找到 %s 个评价，总数: %s", len(reviews), total)
        return reviews, total

    def get_reviews_by_user(self, user_id, skip=0, limit=100):
        """获取用户的评价列表"""
        logger.debug("获取用户评价列表: user_id=%s, skip=%s, limit=%s", user_id, skip, limit)

        query = self.db.query(Review).filter(Review.user_id == user_id)
        total = query.count()
        reviews = (
            query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
        )

        logger.debug("找到 %s 个评价，总数: %s", len(reviews), total)
        return reviews, total

    def get_user_review_for_skill(self, user_id, skill_id):
        """获取用户对特定技能的评价"""
        logger.debug("获取用户对技能的评价: user_id=%s, skill_id=%s", user_id, skill_id)
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id, Review.skill_id == skill_id)
            .first()
        )

    def create_review(self, user_id, review_data):
        """创建评价"""
        logger.info("创建评价: user_id=%s, skill_id=%s", user_id, review_data.skill_id)

        # 检查技能是否存在
        skill = self.db.query(Skill).filter(Skill.id == review_data.skill_id).first()
        if not skill:
            raise ValueError("技能不存在")

        # 检查用户是否已经评价过该技能
        existing = self.get_user_review_for_skill(user_id, review_data.skill_id)
        if existing:
            raise ValueError("您已经评价过该技能")

        db_review = Review(
            skill_id=review_data.skill_id,
            user_id=user_id,
            rating=review_data.rating,
            comment=review_data.comment,
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)

        # 更新技能评分
        self._update_skill_rating(review_data.skill_id)

        # 记录评价的贡献度
        contribution_service = ContributionService(self.db)
        contribution_service.log_contribution(
            user_id=user_id,
            action_type=ActionType.WRITE_REVIEW,
            description=f"评价技能: {skill.name}",
            related_id=db_review.id,
        )

        logger.info("评价创建成功: id=%s", db_review.id)
        return db_review

    def update_review(self, review_id, user_id, review_data):
        """更新评价"""
        logger.info("更新评价: review_id=%s", review_id)

        db_review = self.get_review(review_id)
        if not db_review:
            logger.warning("评价不存在: review_id=%s", review_id)
            return None

        # 检查是否是评价的作者
        if db_review.user_id != user_id:
            raise ValueError("您没有权限修改此评价")

        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_review, field, value)

        self.db.commit()
        self.db.refresh(db_review)

        # 更新技能评分
        self._update_skill_rating(db_review.skill_id)

        logger.info("评价更新成功: review_id=%s", review_id)
        return db_review

    def delete_review(self, review_id, user_id):
        """删除评价"""
        logger.info("删除评价: review_id=%s", review_id)

        db_review = self.get_review(review_id)
        if not db_review:
            logger.warning("评价不存在: review_id=%s", review_id)
            return False

        # 检查是否是评价的作者
        if db_review.user_id != user_id:
            raise ValueError("您没有权限删除此评价")

        skill_id = db_review.skill_id
        self.db.delete(db_review)
        self.db.commit()

        # 更新技能评分
        self._update_skill_rating(skill_id)

        logger.info("评价删除成功: review_id=%s", review_id)
        return True

    def _update_skill_rating(self, skill_id):
        """更新技能的平均评分"""
        logger.debug("更新技能评分: skill_id=%s", skill_id)

        # 计算平均评分
        result = (
            self.db.query(func.avg(Review.rating).label("avg_rating"))
            .filter(Review.skill_id == skill_id)
            .first()
        )

        avg_rating = float(result.avg_rating) if result.avg_rating else 0.0

        # 更新技能的评分
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            skill.rating = round(avg_rating, 2)
            self.db.commit()
            self.db.refresh(skill)

        logger.debug("技能评分已更新: skill_id=%s, rating=%s", skill_id, avg_rating)

    def get_reviews_with_user_info(self, reviews):
        """获取包含用户信息的评价列表"""
        review_dicts = []
        for review in reviews:
            user = self.db.query(User).filter(User.id == review.user_id).first()
            review_dict = {
                "id": review.id,
                "skill_id": review.skill_id,
                "user_id": review.user_id,
                "username": user.username if user else "Unknown",
                "avatar_url": user.avatar_url if user else None,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
            }
            review_dicts.append(review_dict)
        return review_dicts

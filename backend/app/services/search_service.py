"""搜索服务"""
from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.skill import Skill


class SearchService:
    """搜索服务类"""

    @staticmethod
    def search_skills(
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "relevance",
        skip: int = 0,
        limit: int = 50,
    ):
        """
        搜索技能

        Args:
            db: 数据库会话
            query: 搜索关键词
            category: 分类过滤
            tags: 标签列表
            min_rating: 最低评分
            sort_by: 排序方式 (relevance, rating, downloads, newest)
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (技能列表, 总数)
        """
        db_query = db.query(Skill)

        # 构建过滤条件
        filters = []

        # 关键词搜索 - 直接使用 LIKE 查询，兼容 SQLite
        if query:
            db_query = db_query.filter(
                or_(
                    Skill.name.contains(query),
                    Skill.description.contains(query),
                    Skill.category.contains(query),
                    Skill.tags.contains(query),
                )
            )
            if sort_by == "relevance":
                # 简单排序：按下载量降序
                db_query = db_query.order_by(Skill.download_count.desc())

        # 分类过滤
        if category:
            filters.append(Skill.category == category)

        # 标签过滤（支持多个标签，任一匹配）
        if tags and len(tags) > 0:
            tag_filters = [Skill.tags.contains(tag) for tag in tags]
            filters.append(or_(*tag_filters))

        # 最低评分过滤
        if min_rating is not None:
            filters.append(Skill.rating >= min_rating)

        # 应用所有过滤条件
        if filters:
            db_query = db_query.filter(and_(*filters))

        # 获取总数
        total = db_query.count()

        # 应用排序
        if sort_by != "relevance" or not query:
            if sort_by == "rating":
                db_query = db_query.order_by(
                    Skill.rating.desc(), Skill.download_count.desc()
                )
            elif sort_by == "downloads":
                db_query = db_query.order_by(
                    Skill.download_count.desc(), Skill.rating.desc()
                )
            elif sort_by == "newest":
                db_query = db_query.order_by(Skill.created_at.desc())
            else:
                # 默认排序
                db_query = db_query.order_by(
                    Skill.download_count.desc(), Skill.rating.desc()
                )

        # 应用分页
        skills = db_query.offset(skip).limit(limit).all()

        return skills, total

    @staticmethod
    def get_categories(db: Session):
        """获取所有分类"""
        categories = (
            db.query(Skill.category)
            .filter(Skill.category.isnot(None), Skill.category != "")
            .distinct()
            .all()
        )
        return [cat[0] for cat in categories if cat[0]]

    @staticmethod
    def get_all_tags(db: Session):
        """获取所有标签（从 tags 字段中解析）"""
        all_tags = set()
        skills = (
            db.query(Skill.tags).filter(Skill.tags.isnot(None), Skill.tags != "").all()
        )

        for skill in skills:
            if skill.tags:
                # 支持逗号分隔的标签
                tags = [tag.strip() for tag in skill.tags.split(",") if tag.strip()]
                all_tags.update(tags)

        return sorted(list(all_tags))

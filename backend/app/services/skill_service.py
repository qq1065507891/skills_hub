"""技能服务"""
import logging
import os
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import and_, or_

from app.config import get_settings
from app.models.contribution import ActionType
from app.models.publication import Publication, PublicationStatus
from app.models.review import Review
from app.models.skill import Skill
from app.models.skill_version import SkillVersion
from app.services.contribution_service import ContributionService
from app.utils.validators import (
    validate_category,
    validate_license,
    validate_tags,
    validate_version,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class SkillService:
    """技能服务类"""

    def __init__(self, db):
        self.db = db

    def get_skill(self, skill_id):
        """获取单个技能"""
        logger.debug("获取技能: skill_id=%s", skill_id)
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def get_skills(self, skip=0, limit=100, category=None, author_id=None, search=None):
        """获取技能列表"""
        logger.debug("获取技能列表: skip=%s, limit=%s, category=%s", skip, limit, category)

        query = self.db.query(Skill)

        if category:
            query = query.filter(Skill.category == category)

        if author_id:
            query = query.filter(Skill.author_id == author_id)

        if search:
            query = query.filter(
                or_(
                    Skill.name.ilike("%{}%".format(search)),
                    Skill.description.ilike("%{}%".format(search)),
                    Skill.tags.ilike("%{}%".format(search)),
                )
            )

        total = query.count()
        skills = query.offset(skip).limit(limit).all()

        logger.debug("找到 %s 个技能，总数: %s", len(skills), total)
        return skills, total

    def create_skill(self, skill_data, author_id=None):
        """创建技能"""
        logger.info("创建技能：name=%s, author_id=%s", skill_data.name, author_id)

        if not validate_version(skill_data.version):
            raise ValueError("无效的版本号格式：{}".format(skill_data.version))

        if not validate_license(skill_data.license):
            raise ValueError("无效的许可证类型：{}".format(skill_data.license))

        if not validate_category(skill_data.category):
            raise ValueError("无效的分类：{}".format(skill_data.category))

        if not validate_tags(skill_data.tags):
            raise ValueError("无效的标签格式")

        # 使用传入的 author_id 或 skill_data 中的 author_id
        effective_author_id = author_id or skill_data.author_id
        if not effective_author_id:
            raise ValueError("必须指定作者 ID")

        existing = (
            self.db.query(Skill)
            .filter(
                and_(
                    Skill.name == skill_data.name,
                    Skill.author_id == effective_author_id,
                )
            )
            .first()
        )

        if existing:
            raise ValueError("技能名称 '{}' 已存在".format(skill_data.name))

        skill_dict = skill_data.model_dump()
        skill_dict['author_id'] = effective_author_id
        
        db_skill = Skill(**skill_dict)
        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)

        # 记录创建技能的贡献度
        contribution_service = ContributionService(self.db)
        contribution_service.log_contribution(
            user_id=db_skill.author_id,
            action_type=ActionType.CREATE_SKILL,
            description=f"创建技能: {db_skill.name}",
            related_id=db_skill.id,
        )

        logger.info("技能创建成功: id=%s", db_skill.id)
        return db_skill

    def update_skill(self, skill_id, skill_data):
        """更新技能 - 保存历史版本"""
        logger.info("更新技能: skill_id=%s", skill_id)

        db_skill = self.get_skill(skill_id)
        if not db_skill:
            logger.warning("技能不存在: skill_id=%s", skill_id)
            return None

        if skill_data.version is not None and not validate_version(skill_data.version):
            raise ValueError("无效的版本号格式: {}".format(skill_data.version))

        if skill_data.license is not None and not validate_license(skill_data.license):
            raise ValueError("无效的许可证类型: {}".format(skill_data.license))

        if skill_data.category is not None and not validate_category(
            skill_data.category
        ):
            raise ValueError("无效的分类: {}".format(skill_data.category))

        if skill_data.tags is not None and not validate_tags(skill_data.tags):
            raise ValueError("无效的标签格式")

        if skill_data.name is not None and skill_data.name != db_skill.name:
            existing = (
                self.db.query(Skill)
                .filter(
                    and_(
                        Skill.name == skill_data.name,
                        Skill.author_id == db_skill.author_id,
                        Skill.id != skill_id,
                    )
                )
                .first()
            )

            if existing:
                raise ValueError("技能名称 '{}' 已存在".format(skill_data.name))

        # 保存当前版本到历史版本表
        skill_version = SkillVersion(
            skill_id=db_skill.id,
            name=db_skill.name,
            slug_name=db_skill.slug_name,
            description=db_skill.description,
            version=db_skill.version,
            license=db_skill.license,
            category=db_skill.category,
            tags=db_skill.tags,
            download_count=db_skill.download_count,
            rating=db_skill.rating,
            author_id=db_skill.author_id,
            created_at=db_skill.created_at,
            updated_at=db_skill.updated_at,
        )
        self.db.add(skill_version)
        logger.info("保存技能历史版本: skill_id=%s, version=%s", skill_id, db_skill.version)

        update_data = skill_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_skill, field, value)

        self.db.commit()
        self.db.refresh(db_skill)

        # 记录更新技能的贡献度
        contribution_service = ContributionService(self.db)
        contribution_service.log_contribution(
            user_id=db_skill.author_id,
            action_type=ActionType.UPDATE_SKILL,
            description=f"更新技能: {db_skill.name}",
            related_id=db_skill.id,
        )

        logger.info("技能更新成功: skill_id=%s", skill_id)
        return db_skill

    def get_skill_versions(self, skill_id):
        """获取技能的历史版本列表"""
        logger.debug("获取技能历史版本: skill_id=%s", skill_id)
        versions = (
            self.db.query(SkillVersion)
            .filter(SkillVersion.skill_id == skill_id)
            .order_by(SkillVersion.created_at.desc())
            .all()
        )
        return versions

    def get_skill_version(self, version_id):
        """获取单个历史版本详情"""
        logger.debug("获取历史版本详情: version_id=%s", version_id)
        version = (
            self.db.query(SkillVersion)
            .filter(SkillVersion.id == version_id)
            .first()
        )
        return version

    def increment_version_download_count(self, version_id):
        """增加历史版本下载计数"""
        logger.info("增加历史版本下载计数: version_id=%s", version_id)
        
        version = self.get_skill_version(version_id)
        if not version:
            logger.warning("历史版本不存在: version_id=%s", version_id)
            return None
        
        version.download_count += 1
        self.db.commit()
        self.db.refresh(version)
        
        logger.info("历史版本下载计数增加成功: version_id=%s, new_count=%s", version_id, version.download_count)
        return version

    def delete_skill(self, skill_id):
        """删除技能"""
        logger.info("删除技能: skill_id=%s", skill_id)

        db_skill = self.get_skill(skill_id)
        if not db_skill:
            logger.warning("技能不存在: skill_id=%s", skill_id)
            return False

        # 先删除关联的发布记录
        publications = self.db.query(Publication).filter(Publication.skill_id == skill_id).all()
        for pub in publications:
            self.db.delete(pub)
            logger.info("删除关联的发布记录: publication_id=%s", pub.id)

        # 删除关联的评价记录
        reviews = self.db.query(Review).filter(Review.skill_id == skill_id).all()
        for review in reviews:
            self.db.delete(review)
            logger.info("删除关联的评价记录: review_id=%s", review.id)

        self.db.delete(db_skill)
        self.db.commit()

        logger.info("技能删除成功: skill_id=%s", skill_id)
        return True

    def increment_download_count(self, skill_id):
        """增加下载计数"""
        logger.debug("增加下载计数: skill_id=%s", skill_id)

        db_skill = self.get_skill(skill_id)
        if not db_skill:
            return None

        db_skill.download_count += 1
        self.db.commit()
        self.db.refresh(db_skill)

        return db_skill

    # ========== 评价相关方法 ==========

    def get_reviews(self, skill_id):
        """获取技能的评价列表"""
        logger.debug("获取评价列表: skill_id=%s", skill_id)
        reviews = (
            self.db.query(Review)
            .filter(Review.skill_id == skill_id)
            .order_by(Review.created_at.desc())
            .all()
        )
        # 返回字典格式避免修改 SQLAlchemy 实例引发异常
        result = []
        for review in reviews:
            r_dict = {
                "id": review.id,
                "skill_id": review.skill_id,
                "user_id": review.user_id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
            }
            if review.user:
                r_dict["user"] = {
                    "id": review.user.id,
                    "name": review.user.username,
                    "email": review.user.email,
                }
            result.append(r_dict)
        return result

    def create_review(self, skill_id, user_id, review_data):
        """创建评价"""
        logger.info("创建评价: skill_id=%s, user_id=%s", skill_id, user_id)

        # 检查技能是否存在
        skill = self.get_skill(skill_id)
        if not skill:
            raise ValueError("技能不存在")

        # 检查是否已经评价过（可选：每个用户每个技能只能评价一次）
        existing = (
            self.db.query(Review)
            .filter(and_(Review.skill_id == skill_id, Review.user_id == user_id))
            .first()
        )
        if existing:
            raise ValueError("您已经评价过该技能")

        db_review = Review(
            skill_id=skill_id,
            user_id=user_id,
            rating=review_data.rating,
            comment=review_data.comment,
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)

        # 更新技能的平均评分
        self._update_skill_rating(skill_id)

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

    def _update_skill_rating(self, skill_id):
        """更新技能的平均评分"""
        reviews = self.db.query(Review).filter(Review.skill_id == skill_id).all()
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            skill = self.get_skill(skill_id)
            if skill:
                skill.rating = round(avg_rating, 1)
                self.db.commit()

    # ========== 发布相关方法 ==========

    def get_publication(self, publication_id):
        """获取单个发布记录"""
        logger.debug("获取发布记录: publication_id=%s", publication_id)
        return (
            self.db.query(Publication).filter(Publication.id == publication_id).first()
        )

    def get_publications_by_skill(self, skill_id):
        """获取技能的所有发布记录"""
        logger.debug("获取技能发布记录: skill_id=%s", skill_id)
        return (
            self.db.query(Publication)
            .filter(Publication.skill_id == skill_id)
            .order_by(Publication.created_at.desc())
            .all()
        )

    def create_publication(self, skill_id, user_id, notes=None):
        """创建技能发布记录"""
        logger.info("创建发布记录: skill_id=%s, user_id=%s", skill_id, user_id)

        # 检查技能是否存在
        skill = self.get_skill(skill_id)
        if not skill:
            raise ValueError("技能不存在")

        # 检查是否有待审核的发布
        existing_pending = (
            self.db.query(Publication)
            .filter(
                and_(
                    Publication.skill_id == skill_id,
                    Publication.status == PublicationStatus.PENDING,
                )
            )
            .first()
        )
        if existing_pending:
            raise ValueError("该技能已有待审核的发布")

        db_publication = Publication(
            skill_id=skill_id,
            published_by=user_id,
            status=PublicationStatus.PENDING,
            notes=notes,
        )
        self.db.add(db_publication)
        self.db.commit()
        self.db.refresh(db_publication)

        logger.info("发布记录创建成功: id=%s", db_publication.id)
        return db_publication

    def update_publication_status(self, publication_id, status, notes=None):
        """更新发布状态"""
        logger.info("更新发布状态: publication_id=%s, status=%s", publication_id, status)

        db_publication = self.get_publication(publication_id)
        if not db_publication:
            logger.warning("发布记录不存在: publication_id=%s", publication_id)
            return None

        # 验证状态
        try:
            PublicationStatus(status)
        except ValueError:
            raise ValueError("无效的发布状态")

        db_publication.status = status
        if notes is not None:
            db_publication.notes = notes

        if status == PublicationStatus.PUBLISHED:
            db_publication.published_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(db_publication)

        logger.info("发布状态更新成功: publication_id=%s", publication_id)
        return db_publication

    # ========== 文件上传相关方法 ==========

    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        upload_dir = Path(settings.UPLOAD_DIR)
        skill_packages_dir = upload_dir / settings.SKILL_PACKAGES_DIR
        skill_packages_dir.mkdir(parents=True, exist_ok=True)
        return skill_packages_dir

    def _validate_file_extension(self, filename):
        """验证文件扩展名"""
        for ext in settings.ALLOWED_EXTENSIONS:
            if filename.lower().endswith(f".{ext}"):
                return True
        return False

    def _validate_mime_type(self, content_type):
        """验证 MIME 类型"""
        if content_type in settings.ALLOWED_MIME_TYPES:
            return True
        # 也允许一些通用的二进制类型
        allowed_generic = ["application/octet-stream", "binary/octet-stream"]
        return content_type in allowed_generic

    def save_skill_package(self, skill_id, file, filename, content_type=None):
        """保存技能包文件"""
        logger.info("保存技能包: skill_id=%s, filename=%s", skill_id, filename)

        # 检查技能是否存在
        skill = self.get_skill(skill_id)
        if not skill:
            raise ValueError("技能不存在")

        # 验证文件扩展名
        if not self._validate_file_extension(filename):
            raise ValueError(f"不支持的文件格式。仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}")

        # 验证 MIME 类型
        if content_type and not self._validate_mime_type(content_type):
            raise ValueError(f"不支持的文件类型: {content_type}")

        # 确保目录存在
        upload_dir = self._ensure_upload_dir()

        # 生成安全的文件名
        safe_filename = (
            f"skill_{skill_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{filename}"
        )
        file_path = upload_dir / safe_filename

        # 分块读取和写入文件，避免内存问题
        total_size = 0
        chunk_size = 8192  # 8KB chunks

        with open(file_path, "wb") as f:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                # 检查文件大小
                if total_size > settings.MAX_UPLOAD_SIZE:
                    # 删除已写入的部分文件
                    f.close()
                    os.remove(file_path)
                    raise ValueError(
                        f"文件大小超过限制 (最大 {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB)"
                    )
                f.write(chunk)

        logger.info("技能包保存成功: %s, 大小: %s bytes", file_path, total_size)
        return str(file_path)

    def validate_skill_package(self, file_path):
        """验证技能包是否有效"""
        logger.debug("验证技能包: %s", file_path)

        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise ValueError("技能包文件不存在")

            # 检查文件格式并尝试解压
            if file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zf:
                    # 检查是否包含必要的文件（例如 README 或 manifest）
                    file_list = zf.namelist()
                    if len(file_list) == 0:
                        raise ValueError("技能包为空")

            elif file_path.endswith((".tar.gz", ".tgz")):
                with tarfile.open(file_path, "r:gz") as tf:
                    file_list = tf.getnames()
                    if len(file_list) == 0:
                        raise ValueError("技能包为空")

            else:
                raise ValueError("不支持的文件格式")

            return True

        except (zipfile.BadZipFile, tarfile.ReadError) as e:
            logger.error("技能包格式错误: %s", e)
            raise ValueError("无效的技能包文件")

"""应用配置管理"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    APP_NAME: str = "SkillHub API"
    DEBUG: bool = True
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/skillhub"
    TEST_DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/skillhub_test"
    SECRET_KEY: str = ""  # 必须从环境变量获取，无默认值
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/app.log"
    LOG_FORMAT: str = "text"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 5

    # 通知配置
    NOTIFICATION_ENABLED: bool = True
    NOTIFICATION_EMAIL_FROM: Optional[str] = None
    NOTIFICATION_EMAIL_TO: Optional[str] = None
    NOTIFICATION_WEBHOOK_URL: Optional[str] = None

    # CORS 配置
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://frontend:3000"]

    # 技能包上传配置
    UPLOAD_DIR: str = "uploads"
    SKILL_PACKAGES_DIR: str = "skill_packages"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = ["zip", "tar.gz", "tgz"]
    ALLOWED_MIME_TYPES: list = ["application/zip", "application/x-gzip", "application/gzip"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    """获取配置单例"""
    return Settings()

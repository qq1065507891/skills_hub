"""
Alembic 环境配置文件
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import get_settings
from app.dependencies import Base
from app.models import User, Skill, Review, ContributionLog  # noqa: F401

# 这是 Alembic Config 对象，它提供访问 .ini 文件中值的功能
config = context.config

# 解释配置文件中的 Python 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 在这里添加模型的 MetaData 对象
# 用于 'autogenerate' 支持
target_metadata = Base.metadata

# 从配置文件获取数据库 URL
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """以 '离线' 模式运行迁移。

    这会仅使用 URL 配置上下文而不创建 Engine，虽然在这里也可以使用 Engine，但我们只需要 URL 即可。
    通过跳过 Engine 的创建，我们甚至不需要 DBAPI 可用。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以 '在线' 模式运行迁移。

    在这种情况下，我们需要创建一个 Engine 并将连接与上下文关联。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

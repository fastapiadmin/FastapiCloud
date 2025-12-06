"""
Alembic 迁移环境配置文件

该文件定义了数据库迁移的执行环境，包括:
- 数据库连接配置
- 离线/在线迁移模式
- 目标元数据
"""
from alembic.config import Config
from alembic import context
from sqlmodel import SQLModel
from logging.config import fileConfig

from app.config import settings
from core.database import engine


# 获取Alembic配置对象
config: Config = context.config

# 如果配置了日志文件，则加载日志配置
if config.config_file_name is not None:
    fileConfig(fname=config.config_file_name)

# 设置SQLModel的元数据作为迁移目标，所有SQLModel类都会自动注册到这里
from services.admin.app.models.user import *
target_metadata = SQLModel.metadata

# 配置数据库连接URL
config.set_main_option(name="sqlalchemy.url", value=f"sqlite:///{settings.db.BASE_DIR.joinpath(settings.db.SQLITE_DB_NAME)}?check_same_thread=False", )


def run_migrations_offline() -> None:
    """
    离线模式执行数据库迁移
    
    当数据库连接不可用时使用此模式(如CI/CD环境)
    
    参数:
        url: 数据库连接URL
        target_metadata: SQLModel的元数据
        literal_binds: 设置为True以支持离线模式
        dialect_opts: 数据库方言选项
    """
    url: str | None = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # 在事务中执行迁移
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式执行数据库迁移
    
    使用数据库连接执行迁移，适用于开发和生产环境
    
    参数:
        connection: 数据库连接对象
        target_metadata: SQLModel的元数据
    """
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        # 在事务中执行迁移
        with context.begin_transaction():
            context.run_migrations()


# 根据运行模式选择离线或在线迁移
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

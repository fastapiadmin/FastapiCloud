# -*- coding: utf-8 -*-

from typing import Annotated, Any, Generator, TypeAlias
from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from collections.abc import Generator

from core.config import settings
from core.logger import logger


# 同步数据库引擎（兼容旧代码）
engine: Engine = create_engine(
    url=f"sqlite+pysqlite:///{settings.BASE_DIR.joinpath(settings.SQLITE_DB_NAME)}?check_same_thread=False", 
    echo=False
)

SessionLocal = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False
)


def get_db() -> Generator[Session, Any, None]:
    """
    获取同步数据库会话（兼容旧代码）
    
    Yields:
        Session: 数据库会话
    """
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


async def create_db_and_tables() -> None:
    """
    创建数据库表
    """
    try:
        SQLModel.metadata.create_all(bind=engine)    
        logger.info("数据库表创建成功")
        from apps.api.model import User
        # 创建默认用户
        from core.security import set_password_hash
        default_user = User(
            name="管理员",
            username="admin",
            password=set_password_hash("123456"),
            status=True,
            is_superuser=True
        )
        with SessionLocal() as session:
            # 检查默认用户是否已存在
            existing_user = session.exec(
                select(User).where(User.username == default_user.username)
            ).first()
            if not existing_user:
                session.add(default_user)
                session.commit()
                logger.info("默认用户创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise


DB: TypeAlias = Annotated[Session, Depends(get_db)]
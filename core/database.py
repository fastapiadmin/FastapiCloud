# -*- coding: utf-8 -*-

import time
from typing import Any, Generator
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.engine.base import Engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from collections.abc import Generator

from config import settings
from .logger import logger


# 同步数据库引擎（兼容旧代码）
engine: Engine = create_engine(
    url=f"sqlite:///{settings.BASE_DIR.joinpath(settings.SQLITE_DB_NAME)}?check_same_thread=False", 
    echo=False
)

SessionLocal = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False
)

# 连接监控事件
@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """连接创建事件"""
    connection_record.info["start_time"] = time.time()
    logger.debug(f"数据库连接创建: {connection_record}")

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """连接检出事件"""
    connection_record.info["checkout_time"] = time.time()
    logger.debug(f"数据库连接检出: {connection_record}")

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_connection, connection_record):
    """连接检入事件"""
    checkout_time = connection_record.info.pop("checkout_time", None)
    if checkout_time:
        duration = time.time() - checkout_time
        if duration > 5.0:  # 慢查询警告阈值
            logger.warning(f"数据库连接使用时间过长: {duration:.2f}秒")
    logger.debug(f"数据库连接检入: {connection_record}")


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
        from app.api.v1.model import User
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

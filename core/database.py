# -*- coding: utf-8 -*-

"""
统一数据库访问层
提供一致的数据库访问接口，支持同步和异步操作
"""
from typing import Any, Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine.base import Engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from collections.abc import Generator
import time

from app.config import settings
from .logger import logger


# 同步数据库引擎（兼容旧代码）
engine: Engine = create_engine(
    url=f"sqlite:///{settings.db.BASE_DIR.joinpath(settings.db.SQLITE_DB_NAME)}?check_same_thread=False", 
    echo=settings.db.DB_ECHO
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
        finally:
            session.close()


async def create_db_and_tables() -> None:
    """
    创建数据库表
    """
    try:
        SQLModel.metadata.create_all(bind=engine)    
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise

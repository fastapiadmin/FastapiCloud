# -*- coding: utf-8 -*-

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    日志拦截处理器：将所有 Python 标准日志重定向到 Loguru
    
    工作原理：
    1. 继承自 logging.Handler
    2. 重写 emit 方法处理日志记录
    3. 将标准库日志转换为 Loguru 格式
    """
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        处理日志记录
        
        Args:
            record: 日志记录对象
        """
        # 获取对应的 Loguru 级别（如果存在）
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者源码位置
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    log_format: Optional[str] = None
) -> None:
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录路径
        log_level: 日志级别
        log_format: 日志格式
    """
    # 移除默认处理器
    logger.remove()
    
    # 定义默认日志格式
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    
    # 配置控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        colorize=True
    )
    
    # 如果指定了日志目录，配置文件输出
    if log_dir:
        # 确保日志目录存在
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置常规日志文件
        logger.add(
            str(log_dir / "info.log"),
            format=log_format,
            level=log_level,
            rotation="00:00",
            retention="30 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
        
        # 配置错误日志文件
        logger.add(
            str(log_dir / "error.log"),
            format=log_format,
            level="ERROR",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
    
    # 配置标准库日志重定向
    logging.basicConfig(
        handlers=[InterceptHandler()], 
        level=getattr(logging, log_level.upper()),
        force=True
    )


def get_logger(name: Optional[str] = None):
    """
    获取日志记录器
    
    Args:
        name: 记录器名称
        
    Returns:
        logger: Loguru记录器实例
    """
    return logger


# 默认导出
__all__ = ["setup_logging", "get_logger", "logger"]
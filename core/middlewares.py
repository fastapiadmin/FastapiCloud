# -*- coding: utf-8 -*-

"""
统一中间件模块
提供一致的中间件处理机制，包括请求日志、跨域处理、安全头部和速率限制等
"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from typing import Awaitable, Callable, Optional, Dict, Set
import time
import uuid
import hashlib

from .logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        处理请求和响应日志
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"请求开始 [{request_id}]", extra={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown",
            "request_id": request_id
        })
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(f"请求完成 [{request_id}]", extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
                "request_id": request_id
            })
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 记录异常信息
            logger.error(f"请求异常 [{request_id}]: {str(e)}", extra={
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "request_id": request_id
            })
            raise


class CORSMiddlewareConfig:
    """CORS中间件配置"""
    
    def __init__(
        self,
        allow_origins: list = ["*"],
        allow_credentials: bool = True,
        allow_methods: list = ["*"],
        allow_headers: list = ["*"],
        expose_headers: list = [],
        max_age: int = 600
    ):
        """
        初始化CORS配置
        
        Args:
            allow_origins: 允许的源
            allow_credentials: 是否允许凭证
            allow_methods: 允许的方法
            allow_headers: 允许的头部
            expose_headers: 暴露的头部
            max_age: 预检请求缓存时间
        """
        self.allow_origins = allow_origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.expose_headers = expose_headers
        self.max_age = max_age


def register_middleware_handler(
    app: FastAPI,
    cors_config: Optional[CORSMiddlewareConfig] = None,
    enable_gzip: bool = True,
    enable_trusted_hosts: bool = True,
    trusted_hosts: list = ["*"],
    enable_request_logging: bool = True,
    enable_security_headers: bool = True,
    enable_rate_limit: bool = True
) -> None:
    """
    注册中间件处理器
    
    Args:
        app: FastAPI应用实例
        cors_config: CORS配置
        enable_gzip: 是否启用GZIP压缩
        enable_trusted_hosts: 是否启用受信任主机检查
        trusted_hosts: 受信任的主机列表
        enable_request_logging: 是否启用请求日志
        enable_security_headers: 是否启用安全头部
        enable_rate_limit: 是否启用速率限制
    """
    
    # 注册请求日志中间件
    if enable_request_logging:
        app.add_middleware(RequestLoggingMiddleware)
    
    # 注册CORS中间件
    if cors_config is None:
        cors_config = CORSMiddlewareConfig()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allow_origins,
        allow_credentials=cors_config.allow_credentials,
        allow_methods=cors_config.allow_methods,
        allow_headers=cors_config.allow_headers,
        expose_headers=cors_config.expose_headers,
        max_age=cors_config.max_age
    )
    
    # 注册GZIP压缩中间件
    if enable_gzip:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 注册受信任主机中间件
    if enable_trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# 默认导出
__all__ = [
    "RequestLoggingMiddleware",
    "CORSMiddlewareConfig",
    "register_middleware_handler"
]
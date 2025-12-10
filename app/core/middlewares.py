# -*- coding: utf-8 -*-

import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from collections.abc import Awaitable, Callable

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


def register_middleware_handler(app: FastAPI) -> None:
    """
    注册中间件处理器
    
    Args:
        app: FastAPI应用实例
    """
    # 注册请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    
    # 注册CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[],
        max_age=600
    )
    
    # 注册GZIP压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 注册受信任主机中间件
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


# 默认导出
__all__ = [
    "RequestLoggingMiddleware",
    "register_middleware_handler"
]
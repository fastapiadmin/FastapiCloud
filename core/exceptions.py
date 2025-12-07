# -*- coding: utf-8 -*-

import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextvars import ContextVar

from core.response import ErrorResponse
from .logger import get_logger

# 创建请求ID上下文变量
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

# 获取日志记录器
logger = get_logger("exceptions")


class AppException(Exception):
    """应用程序基础异常类"""
    
    def __init__(
        self, 
        message: str = "应用程序异常", 
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """
        初始化应用程序异常
        
        Args:
            message: 异常消息
            status_code: HTTP状态码
            error_code: 错误代码
            details: 详细信息
            request_id: 请求ID
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"HTTP_{status_code}"
        self.details = details or {}
        self.request_id = request_id or request_id_ctx_var.get()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict: 异常信息字典
        """
        return {
            "message": self.message,
            "status_code": self.status_code,
            "error_code": self.error_code,
            "details": self.details,
            "request_id": self.request_id
        }


class ValidationError(AppException):
    """数据验证异常"""
    
    def __init__(
        self, 
        message: str = "数据验证失败", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(AppException):
    """身份验证异常"""
    
    def __init__(self, message: str = "身份验证失败"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(AppException):
    """权限异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(AppException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "资源未找到"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND_ERROR"
        )


def register_exception_handlers(app) -> None:
    """
    注册全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """
        请求中间件：添加请求ID到上下文
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理函数
        
        Returns:
            Response: 响应对象
        """
        # 从请求头获取或生成请求ID
        request_id = request.headers.get("X-Request-ID") or f"req-{id(request)}"
        
        # 设置请求ID到上下文变量
        request_id_ctx_var.set(request_id)
        
        # 设置请求ID到请求对象
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """处理应用程序异常"""
        # 获取请求ID
        request_id = getattr(request.state, "request_id", request_id_ctx_var.get())
        
        # 记录异常日志
        logger.error(f"应用程序异常: {exc.message}", extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "details": exc.details,
            "request_id": request_id
        })
        
        # 构建响应
        response_data = {
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "request_id": request_id
        }
        
        return ErrorResponse(
            data=response_data,
            message=exc.message,
            status_code=exc.status_code
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """处理HTTP异常"""
        # 获取请求ID
        request_id = getattr(request.state, "request_id", request_id_ctx_var.get())
        
        # 处理exc.detail，避免loguru格式化错误
        detail_str = str(exc.detail)
        
        # 记录异常日志
        logger.warning("HTTP异常: {}", detail_str, extra={
            "status_code": exc.status_code,
            "headers": exc.headers,
            "request_id": request_id
        })
        
        # 构建响应
        response_data = {
            "error": f"HTTP_{exc.status_code}",
            "message": detail_str,
            "request_id": request_id
        }
        
        return ErrorResponse(
            data=response_data,
            message=detail_str,
            status_code=exc.status_code
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """处理Starlette HTTP异常"""
        # 获取请求ID
        request_id = getattr(request.state, "request_id", request_id_ctx_var.get())
        
        # 记录异常日志
        logger.warning(f"Starlette HTTP异常: {exc.detail}", extra={
            "status_code": exc.status_code,
            "request_id": request_id
        })
        
        # 构建响应
        response_data = {
            "error": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "request_id": request_id
        }
        
        return ErrorResponse(
            data=response_data,
            message=str(exc.detail),
            status_code=exc.status_code
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理通用异常"""
        # 获取请求ID
        request_id = getattr(request.state, "request_id", request_id_ctx_var.get())
        
        # 记录异常日志（包含完整堆栈）
        logger.error(f"未处理的异常: {str(exc)}", extra={
            "request_id": request_id,
            "stacktrace": traceback.format_exc()
        }, exc_info=True)
        
        # 构建响应
        response_data = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "request_id": request_id,
            "details": {"error": str(exc)}
        }
        
        return ErrorResponse(
            data=response_data,
            message="服务器内部错误",
            status_code=500
        )


# 默认导出
__all__ = [
    "AppException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "register_exception_handlers"
]
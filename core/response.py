# -*- coding: utf-8 -*-

from typing import Union, Dict, Any
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse


class BaseResponse:
    """基础响应类"""
    
    def __init__(self, code: int, message: str, data: Any = None):
        """
        初始化基础响应
        
        Args:
            code: 响应状态码
            message: 响应消息
            data: 响应数据
        """
        self.code = code
        self.message = message
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict: 响应字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


class SuccessResponse(JSONResponse):
    """成功响应类"""
    
    def __init__(
        self,
        data: Any = None,
        message: str = "成功",
        status_code: int = status.HTTP_200_OK,
    ) -> None:
        """
        初始化成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            status_code: HTTP状态码
        """
        content = BaseResponse(
            code=status_code,
            message=message,
            data=data
        ).to_dict()
        
        super().__init__(content=content, status_code=status_code)


class ErrorResponse(JSONResponse):
    """错误响应类"""
    
    def __init__(
        self,
        data: Any = None,
        message: str = "失败",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        """
        初始化错误响应
        
        Args:
            data: 响应数据
            message: 响应消息
            status_code: HTTP状态码
        """
        content = BaseResponse(
            code=status_code,
            message=message,
            data=data
        ).to_dict()
        
        super().__init__(content=content, status_code=status_code)


class ExceptResponse(HTTPException):
    """异常响应类"""
    
    def __init__(
        self,
        data: Any = None,
        message: str = "发生异常",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        """
        初始化异常响应
        
        Args:
            data: 响应数据
            message: 响应消息
            status_code: HTTP状态码
        """
        content = BaseResponse(
            code=status_code,
            message=message,
            data=data
        ).to_dict()
        
        super().__init__(status_code=status_code, detail=content)


def create_response(
    success: bool = True,
    data: Any = None,
    message: str = "",
    status_code: int = 200
) -> Union[SuccessResponse, ErrorResponse]:
    """
    创建统一响应
    
    Args:
        success: 是否成功
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        Union[SuccessResponse, ErrorResponse]: 响应对象
    """
    if success:
        return SuccessResponse(
            data=data,
            message=message or "成功",
            status_code=status_code
        )
    else:
        return ErrorResponse(
            data=data,
            message=message or "失败",
            status_code=status_code
        )
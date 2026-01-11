# -*- coding: utf-8 -*-

from typing import Any
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from core.base import BaseResponse


class SuccessResponse(JSONResponse):
    """成功响应类"""
    
    def __init__(
        self,
        code: int = status.HTTP_200_OK,
        msg: str = "成功",
        data: Any = None,
    ) -> None:
        content = BaseResponse(
            code=code,
            msg=msg,
            data=data
        ).model_dump()
        super().__init__(content=content, status_code=code)


class ErrorResponse(JSONResponse):
    """错误响应类"""
    
    def __init__(
        self,
        code: int = status.HTTP_400_BAD_REQUEST,
        msg: str = "失败",
        data: Any = None,
    ) -> None:
        content = BaseResponse(
            code=code,
            msg=msg,
            data=data
        ).model_dump()
        super().__init__(content=content, status_code=code)


class ExceptResponse(HTTPException):
    """异常响应类"""
    
    def __init__(
        self,
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        msg: str = "服务异常",
        data: Any = None,
    ) -> None:
        content = BaseResponse(
            code=code,
            msg=msg,
            data=data
        ).model_dump()
        super().__init__(status_code=code, detail=content)

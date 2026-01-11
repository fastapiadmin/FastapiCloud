# -*- coding: utf-8 -*-

from typing import Any
from fastapi import status
from sqlmodel import SQLModel, Field
from datetime import datetime


class Base(SQLModel):
    """所有模型的基类"""
    id: int | None = Field(default=None, primary_key=True, index=True)
    created_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False, description="创建时间")
    updated_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False, description="更新时间")


class JWTPayloadSchema(SQLModel):
    """JWT载荷模型"""
    sub: str
    exp: datetime


class JWTOutSchema(SQLModel):
    """JWT响应模型"""
    access_token: str
    token_type: str
    expires_in: float


class BaseResponse(SQLModel):
    """基础响应类"""
    code: int = Field(default=status.HTTP_200_OK, description="HTTP状态码")
    msg: str = Field(default="成功", description="响应消息")
    data: Any = Field(default=None, description="响应数据")

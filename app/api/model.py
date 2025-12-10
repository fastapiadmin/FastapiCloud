# -*- coding: utf-8 -*-

from fastapi import Query
from sqlmodel import Field, SQLModel
from core.base import Base

class UserInSchema(SQLModel):
    """用户模型"""
    name: str = Field(default=..., description="昵称")
    username: str = Field(default=..., description="账号")
    password: str = Field(default=..., description="密码")
    status: bool = Field(default=..., description="状态(True:启用 False:禁用)")
    description: str | None = Field(default=None, max_length=255, description="备注")


class User(Base, UserInSchema, table=True):
    """系统用户表，存储平台所有用户信息"""
    is_superuser: bool = Field(default=False, description="是否超级管理员")


class UserQuerySchema(SQLModel):
    """用户查询模型"""
    name: str | None = Query(default=None, description="昵称")

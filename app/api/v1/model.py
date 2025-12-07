# -*- coding: utf-8 -*-

from sqlmodel import Field
from core.base import Base


class User(Base, table=True):
    """系统用户表，存储平台所有用户信息"""
    name: str = Field(index=True, nullable=False, max_length=50, description="名称")
    username: str = Field(unique=True, max_length=50, description="登录账号")
    password: str = Field(max_length=255, description="哈希密码")
    is_superuser: bool = Field(default=False, description="是否超级管理员")
    status: bool = Field(default=..., description="状态(True:启用 False:禁用)")
    description: str | None = Field(default=None, max_length=255, description="备注")

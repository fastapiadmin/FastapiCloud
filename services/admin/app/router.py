# -*- coding: utf-8 -*-

from fastapi import APIRouter
from .api.user import router

app = APIRouter()

# 注册路由
app.include_router(
    router, 
    prefix="/admin", 
    tags=["系统接口"],
    responses={
        200: {"description": "成功"},
        201: {"description": "创建成功"},
        300: {"description": "重定向"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权访问"},
        403: {"description": "权限不足"},
        404: {"description": "资源未找到"},
        500: {"description": "服务器内部错误"}
    })
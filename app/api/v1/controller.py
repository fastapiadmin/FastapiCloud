# -*- coding: utf-8 -*-

from pathlib import Path
from sqlmodel import Session
from typing import Dict, Union
from fastapi import Form, Request, APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi_pagination import Page, Params

from core.logger import logger
from core.dependencies import get_current_user
from core.database import get_db
from core.response import ExceptResponse, ErrorResponse, SuccessResponse
from core.base import JWTOutSchema
from .model import User
from .schema import UserQuerySchema, UserInSchema
from .service import UserService

# 创建API路由器
router = APIRouter(prefix="", tags=["用户管理"])
templates = Jinja2Templates(directory="templates")


@router.get("/", summary="首页页面")
async def home(
    request: Request
):
    return templates.TemplateResponse(request=request, name="home.html")

@router.post(
    path="/login", 
    summary="用户登录", 
    response_model=JWTOutSchema,
    status_code=status.HTTP_200_OK,
    description="用户登录接口，验证用户名和密码并返回JWT令牌"
)
async def login(
    request: Request,
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependency=get_db),
) -> Union[JSONResponse, Dict]:
    """用户登录"""
    try:
        # 用户认证
        # 创建访问令牌
        login_token: JWTOutSchema = UserService.login(db, login_form)

        # 如果是文档请求，则直接返回模型
        if "docs" in request.headers.get("referer", ""):
            return login_token.model_dump()

        return SuccessResponse(data=login_token.model_dump())
    except Exception as e:
        logger.error(f"登录异常: {e}", exc_info=True)
        raise ExceptResponse(message="登录失败，请稍后重试")

@router.post(
    path="/logout", 
    summary="用户登出", 
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="用户登出系统",
    dependencies=[Depends(dependency=get_current_user)]
)
async def logout(
    request: Request,
    token: str = Form(default=..., description="访问令牌"),
    db: Session = Depends(dependency=get_db),
    current_user: User = Depends(get_current_user)
) -> JSONResponse:
    try:
        user: User | None = UserService.logout(db, token)
        if not user:
            return ErrorResponse(message="用户不存在")

        request.scope["user_id"] = None

        return SuccessResponse(data=True)

    except Exception as e:
        logger.error(f"用户{current_user.username}登出异常: {e}", exc_info=True)
        raise ExceptResponse(message="登出失败，请稍后重试")

@router.get(
    path="/users", 
    summary="获取用户列表", 
    response_model=Page[User],
    status_code=status.HTTP_200_OK,
    description="获取用户分页列表，支持筛选和排序",
    dependencies=[Depends(dependency=get_current_user)]
)
async def get_users(
    query: UserQuerySchema = Depends(),
    params: Params = Depends(),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    try:
        users = UserService.user_list(db, query, params)
        return SuccessResponse(data=users.dict())

    except Exception as e:
        logger.error(f"查询用户列表异常: {e}", exc_info=True)
        raise ExceptResponse(message="查询用户列表失败，请稍后重试")

@router.post(
    path="/user", 
    summary="创建用户", 
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    description="创建新用户接口",
    dependencies=[Depends(dependency=get_current_user)]
)
async def create_user(
    data: UserInSchema = Depends(),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """创建用户"""
    try:
        user: User | None = UserService.user_create(db, data)
        if not user:
            return ErrorResponse(message="用户已存在", status_code=status.HTTP_400_BAD_REQUEST)

        return SuccessResponse(data=user.model_dump(), message="用户创建成功", status_code=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"创建用户异常: {e}", exc_info=True)
        raise ExceptResponse(message="用户创建失败，请稍后重试")

@router.get(
    path="/user/{id}", 
    summary="获取用户详情", 
    response_model=User,
    status_code=status.HTTP_200_OK,
    description="获取指定用户的详细信息",
    dependencies=[Depends(dependency=get_current_user)]
)
async def get_user_detail(
    id: int = Path(default=..., description="用户ID",ge=1),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """获取用户详情"""
    try:
        user: User | None = UserService.user_detail(db, id)
        if not user:
            return ErrorResponse(message="用户不存在", status_code=status.HTTP_404_NOT_FOUND)

        return SuccessResponse(data=user.model_dump())

    except Exception as e:
        logger.error(f"获取用户详情异常: {e}", exc_info=True)
        raise ExceptResponse(message="获取用户详情失败，请稍后重试")

@router.put(
    path="/user/{id}", 
    summary="更新用户信息", 
    response_model=User,
    status_code=status.HTTP_200_OK,
    description="更新指定用户的信息",
    dependencies=[Depends(dependency=get_current_user)]
)
async def update_user(
    data: UserInSchema = Depends(),
    id: int = Path(default=..., description="用户ID",ge=1),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """更新用户"""
    try:
        user: User | None = UserService.user_update(db, id, data)
        if not user:
            return ErrorResponse(message="用户不存在或用户名已存在", status_code=status.HTTP_400_BAD_REQUEST)

        return SuccessResponse(data=user.model_dump(), message="用户更新成功")

    except Exception as e:
        logger.error(f"更新用户异常: {e}", exc_info=True)
        raise ExceptResponse(message="更新用户失败，请稍后重试")

@router.delete(
    path="/user/{id}", 
    summary="删除用户", 
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="删除指定用户",
    dependencies=[Depends(dependency=get_current_user)]
)
async def delete_user(
    id: int = Path(default=..., description="用户ID",ge=1),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """删除用户"""
    try:
        user: User | None = UserService.user_delete(db, id)
        if not user:
            return ErrorResponse(message="用户不存在", status_code=status.HTTP_404_NOT_FOUND)

        return SuccessResponse(data={"deleted": True}, message="用户删除成功")

    except Exception as e:
        logger.error(f"删除用户异常: {e}", exc_info=True)
        raise ExceptResponse(message="删除用户失败，请稍后重试")

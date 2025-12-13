# -*- coding: utf-8 -*-

from fastapi_pagination.default import Page
from app.api.model import User
from sqlmodel import Session
from typing import Dict, Union
from fastapi import Request, APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, Params

from app.core.logger import logger
from app.core.database import get_db, DB
from app.core.response import BaseResponse, ExceptResponse, ErrorResponse, SuccessResponse
from app.core.base import JWTOutSchema
from ..dependencies import get_current_user, CurrentUser
from ..model import User, UserQuerySchema, UserInSchema
from ..service import UserService

# 创建API路由器
router = APIRouter(prefix="/api", tags=["用户管理"])

@router.get("/health-check")
async def health_check() -> bool:
    return True

@router.post(
    path="/login", 
    summary="用户登录", 
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="用户登录接口，验证用户名和密码并返回JWT令牌"
)
async def login(
    request: Request,
    db: DB,
    login_form: OAuth2PasswordRequestForm = Depends(),
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
        raise ExceptResponse(msg="登录失败，请稍后重试")

@router.post(
    path="/logout", 
    summary="用户登出", 
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="用户登出系统",
)
async def logout(
    request: Request,
    db: DB,
    current_user: CurrentUser,
) -> JSONResponse:
    try:
        UserService.logout(db, current_user)
        request.scope["user_id"] = None
        return SuccessResponse(data=True)
    except ValueError as e:
        logger.error(f"用户{current_user.username}登出参数错误: {e}")
        return ErrorResponse(msg=str(e), code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"用户{current_user.username}登出异常: {e}", exc_info=True)
        raise ExceptResponse(msg="登出失败，请稍后重试")

@router.get(
    path="/users", 
    summary="获取用户列表", 
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="获取用户分页列表，支持筛选和排序",
    dependencies=[Depends(get_current_user)]
)
async def get_users(
    db: DB,
    query: UserQuerySchema = Depends(),
    params: Params = Depends(),
) -> JSONResponse:
    try:
        users: Page[User] = UserService.user_list(db, query, params)
        return SuccessResponse(data=users.dict())
    except Exception as e:
        logger.error(f"查询用户列表异常: {e}", exc_info=True)
        raise ExceptResponse(msg="查询用户列表失败，请稍后重试")

@router.post(
    path="/user", 
    summary="创建用户", 
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    description="创建新用户接口",
    dependencies=[Depends(get_current_user)]
)
async def create_user(
    db: DB,
    data: UserInSchema = Depends(),
) -> JSONResponse:
    """创建用户"""
    try:
        user: User = UserService.user_create(db, data)
        return SuccessResponse(data=user.model_dump(), msg="用户创建成功", code=status.HTTP_201_CREATED)
    except ValueError as e:
        logger.error(f"创建用户参数错误: {e}")
        return ErrorResponse(msg=str(e), code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"创建用户异常: {e}", exc_info=True)
        raise ExceptResponse(msg="用户创建失败，请稍后重试")

@router.get(
    path="/user/{id}", 
    summary="获取用户详情", 
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="获取指定用户的详细信息",
    dependencies=[Depends(get_current_user)]
)
async def get_user_detail(
    db: DB,
    id: int = Path(default=..., description="用户ID",ge=1),
) -> JSONResponse:
    """获取用户详情"""
    try:
        user: User = UserService.user_detail(db, id)
        return SuccessResponse(data=user.model_dump())
    except ValueError as e:
        logger.error(f"获取用户详情参数错误: {e}")
        return ErrorResponse(msg=str(e), code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"获取用户详情异常: {e}", exc_info=True)
        raise ExceptResponse(msg="获取用户详情失败，请稍后重试")

@router.put(
    path="/user/{id}", 
    summary="更新用户信息", 
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="更新指定用户的信息",
    dependencies=[Depends(get_current_user)]
)
async def update_user(
    data: UserInSchema = Depends(),
    id: int = Path(default=..., description="用户ID",ge=1),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """更新用户"""
    try:
        user: User = UserService.user_update(db, id, data)
        return SuccessResponse(data=user.model_dump(), msg="用户更新成功")
    except ValueError as e:
        logger.error(f"更新用户参数错误: {e}")
        return ErrorResponse(msg=str(e), code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"更新用户异常: {e}", exc_info=True)
        raise ExceptResponse(msg="更新用户失败，请稍后重试")

@router.delete(
    path="/user/{id}", 
    summary="删除用户", 
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="删除指定用户",
    dependencies=[Depends(get_current_user)]
)
async def delete_user(
    db: DB,
    id: int = Path(default=..., description="用户ID",ge=1),
) -> JSONResponse:
    """删除用户"""
    try:
        user: User = UserService.user_delete(db, id)
        return SuccessResponse(data={"deleted": True, "user": user.model_dump()}, msg="用户删除成功")
    except ValueError as e:
        logger.error(f"删除用户参数错误: {e}")
        return ErrorResponse(msg=str(e), code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"删除用户异常: {e}", exc_info=True)
        raise ExceptResponse(msg="删除用户失败，请稍后重试")

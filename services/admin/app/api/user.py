# -*- coding: utf-8 -*-

import json
from pathlib import Path
from fastapi import File, Form, Query, Request, APIRouter, Depends, Path, UploadFile
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, desc, func, select, asc, and_
from typing import Dict, Union
from datetime import datetime, timedelta
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi import status

from app.config import settings
from core.logger import logger
from core.dependencies import get_current_user
from core.database import get_db
from core.response import ExceptResponse, ErrorResponse, SuccessResponse
from core.security import (
    create_access_token,
    decode_access_token,
    set_password_hash,
    verify_password,
)
from core.base import (
    JWTPayloadSchema,
    JWTOutSchema
)
from ..models.user import User
from ..schemas.user import (
    UserQuerySchema,
    UserInSchema,
    UserOutSchema,
)

# 创建API路由器
router: APIRouter = APIRouter(
    prefix="",
    tags=["用户管理"]
)


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
        existing_obj: User | None = db.exec(select(User).where(User.username == login_form.username)).first()
        if not existing_obj:
            logger.warning(f"用户{login_form.username}不存在")
            return ErrorResponse(message="用户不存在", status_code=status.HTTP_404_NOT_FOUND)
        if not existing_obj.status:
            logger.warning(f"用户{login_form.username}已禁用")
            return ErrorResponse(message="用户已禁用", status_code=status.HTTP_403_FORBIDDEN)
        if not verify_password(plain_password=login_form.password, hashed_password=existing_obj.password):
            logger.warning(f"用户 {login_form.username} 密码错误")
            return ErrorResponse(message="密码错误", status_code=status.HTTP_401_UNAUTHORIZED)

        access_expires: timedelta = timedelta(
            minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token: str = create_access_token(
            payload=JWTPayloadSchema(
                sub=existing_obj.username,
                exp=datetime.now() + access_expires,
            )
        )

        login_token: JWTOutSchema = JWTOutSchema(
            access_token=access_token,
            token_type=settings.jwt.TOKEN_TYPE,
            expires_in=access_expires.total_seconds()
        )

        logger.info(f"用户{existing_obj.username}登录成功")

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
        jwt_payload: JWTPayloadSchema = decode_access_token(token=token)
        username: str = jwt_payload.sub
        existing_obj: User | None = db.exec(
            select(User).where(User.username == username)
        ).first()
        if not existing_obj:
            logger.warning(f"用户{username}不存在")
            return ErrorResponse(message="用户不存在")
        if not existing_obj.status:
            logger.warning(f"用户{username}已禁用")
            return ErrorResponse(message="用户已禁用")

        request.scope["user_id"] = None

        logger.info(f"{username} 用户退出登录成功")
        return SuccessResponse(data=True)

    except Exception as e:
        logger.error(f"用户{current_user.username}登出异常: {e}", exc_info=True)
        raise ExceptResponse(message="登出失败，请稍后重试")

@router.get(
    path="/users", 
    summary="获取用户列表", 
    response_model=Page[UserOutSchema],
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
        # 构建查询
        sql = select(User)
        if query.name:
            sql = sql.where(User.name.ilike(f"%{query.name}%"))
        sql = sql.order_by(asc(User.id))

        logger.info(f"查询用户列表，参数: {query}")
        return SuccessResponse(data=paginate(db, sql, params))

    except Exception as e:
        logger.error(f"查询用户列表异常: {e}", exc_info=True)
        raise ExceptResponse(message="查询用户列表失败，请稍后重试")

@router.post(
    path="/user", 
    summary="创建用户", 
    response_model=UserOutSchema,
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
        existing_obj: User | None = db.exec(
            select(User).where(User.username == data.username)
        ).first()
        if existing_obj:
            logger.warning(f"用户{data.username}已存在")
            return ErrorResponse(message="用户已存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 创建用户
        new_obj: User = User(**data.model_dump())
        new_obj.password = set_password_hash(data.password)
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)

        logger.info(f"创建用户{new_obj.username}成功")
        return SuccessResponse(data=new_obj, message="用户创建成功", status_code=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"创建用户异常: {e}", exc_info=True)
        raise ExceptResponse(message="用户创建失败，请稍后重试")

@router.get(
    path="/user/{id}", 
    summary="获取用户详情", 
    response_model=UserOutSchema,
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
        existing_obj: User | None = db.exec(select(User).where(User.id == id)).first()
        if not existing_obj:
            logger.warning(f"用户ID {id} 不存在")
            return ErrorResponse(message="用户不存在", status_code=status.HTTP_404_NOT_FOUND)

        logger.info(f"获取用户{existing_obj.username}详情成功")
        return SuccessResponse(data=existing_obj)

    except Exception as e:
        logger.error(f"获取用户详情异常: {e}", exc_info=True)
        raise ExceptResponse(message="获取用户详情失败，请稍后重试")

@router.put(
    path="/user/{id}", 
    summary="更新用户信息", 
    response_model=UserOutSchema,
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
        existing_obj: User | None = db.exec(select(User).where(User.id == id)).first()
        if not existing_obj:
            logger.warning(f"用户ID {id} 不存在")
            return ErrorResponse(message="用户不存在", status_code=status.HTTP_404_NOT_FOUND)

        # 更新用户
        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("password"):
            update_data["password"] = set_password_hash(update_data["password"])

        # 检查用户名是否重复
        if "username" in update_data and update_data["username"] != existing_obj.username:
            existing_user: User | None = db.exec(
                select(User).where(User.username == update_data["username"])
            ).first()
            if existing_user:
                logger.warning(f"用户名{update_data['username']}已存在")
                return ErrorResponse(message="用户名已存在", status_code=status.HTTP_400_BAD_REQUEST)

        # 更新用户信息
        for key, value in update_data.items():
            setattr(existing_obj, key, value)

        db.commit()
        db.refresh(existing_obj)

        logger.info(f"更新用户{existing_obj.username}成功")
        return SuccessResponse(data=existing_obj, message="用户更新成功")

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
        existing_obj: User | None = db.exec(select(User).where(User.id == id)).first()
        if not existing_obj:
            logger.warning(f"用户ID {id} 不存在")
            return ErrorResponse(message="用户不存在", status_code=status.HTTP_404_NOT_FOUND)

        # 删除用户
        db.delete(existing_obj)
        db.commit()

        logger.info(f"删除用户{existing_obj.username}成功")
        return SuccessResponse(data={"deleted": True}, message="用户删除成功")

    except Exception as e:
        logger.error(f"删除用户异常: {e}", exc_info=True)
        raise ExceptResponse(message="删除用户失败，请稍后重试")

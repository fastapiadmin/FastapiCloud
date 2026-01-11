# -*- coding: utf-8 -*-

from typing import Dict
from fastapi import Request, APIRouter, Depends, WebSocket, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page

from core.logger import logger
from core.database import DB
from core.response import BaseResponse, ExceptResponse, ErrorResponse, SuccessResponse
from core.base import JWTOutSchema
from ..dependencies import (
    get_current_user, PaginationParams, LoginForm,
    CurrentUser, UserQuery, UserCreateData, UserUpdateData, UserID
)
from ..model import ChatQuerySchema, User
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
async def login_controller(
    request: Request,
    db: DB,
    login_form: LoginForm,
) -> JSONResponse | Dict:
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
async def logout_controller(
    request: Request,
    current_user: CurrentUser,
) -> JSONResponse:
    try:
        UserService.logout(current_user)
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
async def get_users_controller(
    db: DB,
    query: UserQuery,
    params: PaginationParams,
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
async def create_user_controller(
    db: DB,
    data: UserCreateData,
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
async def get_user_detail_controller(
    db: DB,
    id: UserID,
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
async def update_user_controller(
    data: UserUpdateData,
    id: UserID,
    db: DB,
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
async def delete_user_controller(
    db: DB,
    id: UserID,
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

@router.websocket(
    "/chat/ws", 
    name="WebSocket聊天"
)
async def websocket_chat_controller(
    websocket: WebSocket,
):
    """
    WebSocket聊天接口
    
    ws://127.0.0.1:8001/api/chat/ws
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 流式发送响应
            try:
                async for chunk in UserService.user_chat(query=ChatQuerySchema(message=data)):
                    if chunk:
                        await websocket.send_text(chunk)
            except Exception as e:
                logger.error(f"处理聊天查询出错: {str(e)}")
                await websocket.send_text(f"抱歉，处理您的请求时出现了错误: {str(e)}")
    except Exception as e:
        logger.error(f"WebSocket聊天出错: {str(e)}")
    finally:
        try:
            # 检查WebSocket连接状态，避免重复关闭已关闭的连接
            if websocket.client_state != websocket.client_state.DISCONNECTED:
                await websocket.close()
        except Exception as e:
            logger.debug(f"WebSocket关闭时发生异常(预期行为，服务可能正在关闭): {str(e)}")
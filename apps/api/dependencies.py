# -*- coding: utf-8 -*-

from typing import Annotated
from fastapi import Body, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import Params
from sqlmodel import Session, select

from core.database import get_db
from core.security import decode_access_token
from apps.api.model import User, UserQuerySchema, UserInSchema


# OAuth2密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    username = payload.sub
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# 当前登录用户
CurrentUser = Annotated[User, Depends(get_current_user)]

# 分页参数
PaginationParams = Annotated[Params, Depends()]

# 登录表单
LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]

# 用户查询参数
UserQuery = Annotated[UserQuerySchema, Depends()]

# 用户创建数据
UserCreateData = Annotated[UserInSchema, Body(...)]

# 用户更新数据
UserUpdateData = Annotated[UserInSchema, Body(...)]

# 用户ID路径参数
UserID = Annotated[int, Path(...)]

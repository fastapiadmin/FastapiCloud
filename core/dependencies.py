# -*- coding: utf-8 -*-

"""
依赖注入模块
提供所有路由的依赖函数
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.config import settings
from core.database import get_db
from core.security import decode_access_token
from core.base import User
from sqlmodel import select


# OAuth2密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.service.API_V1_STR}/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户
    从JWT令牌中提取用户名并查询数据库，返回当前用户对象。
    
    Args:
        token: 访问令牌
        db: 数据库会话
        
    Returns:
        User: 当前用户
    """
    try:
        payload = decode_access_token(token)
        username = payload.sub
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"Authenticate": "Bearer"},
        )
    
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"Authenticate": "Bearer"},
        )
    
    return user

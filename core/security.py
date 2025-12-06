# -*- coding: utf-8 -*-

"""
安全相关功能模块
提供密码哈希、JWT令牌生成和验证等功能
"""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings
from core.base import JWTPayloadSchema


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    payload: JWTPayloadSchema,
) -> str:
    """
    创建访问令牌
    
    Args:
        payload: 令牌载荷
        expires_delta: 过期时间增量
        
    Returns:
        str: 访问令牌
    """
    to_encode = payload.model_dump()
    if payload.exp:
        expire = payload.exp
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> JWTPayloadSchema:
    """
    解码访问令牌
    
    Args:
        token: 访问令牌
        
    Returns:
        JWTPayloadSchema: 解码后的令牌载荷
    """
    try:
        payload = jwt.decode(token, settings.jwt.SECRET_KEY, algorithms=[settings.jwt.ALGORITHM])
        return JWTPayloadSchema(**payload)
    except JWTError:
        raise ValueError("无效的令牌")


def set_password_hash(password: str) -> str:
    """
    设置密码哈希
    
    Args:
        password: 原始密码
        
    Returns:
        str: 密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 原始密码
        hashed_password: 密码哈希
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

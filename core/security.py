# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt

from config import settings
from core.base import JWTPayloadSchema


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
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
    # bcrypt限制密码长度为72字节，超过会自动截断，但这里手动截断以避免警告
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 原始密码
        hashed_password: 密码哈希
        
    Returns:
        bool: 密码是否匹配
    """
    plain_bytes = plain_password[:72].encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

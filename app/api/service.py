# -*- coding: utf-8 -*-

from fastapi_pagination import Params, Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select, asc
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm

from core.config import settings
from core.logger import logger
from core.security import (
    create_access_token,
    set_password_hash,
    verify_password,
)
from core.base import JWTPayloadSchema, JWTOutSchema
from .model import User, UserQuerySchema, UserInSchema


class UserService:
    """
    User Service
    """
    @classmethod
    def login(cls, db: Session, login_form: OAuth2PasswordRequestForm) -> JWTOutSchema:
        """用户登录认证"""
        # 用户认证
        existing_obj: User | None = db.exec(select(User).where(User.username == login_form.username)).first()
        if not existing_obj:
            logger.warning(f"用户{login_form.username}不存在")
            raise ValueError(f"用户{login_form.username}不存在")
        if not existing_obj.status:
            logger.warning(f"用户{login_form.username}已禁用")
            raise ValueError(f"用户{login_form.username}已禁用")
        if not verify_password(plain_password=login_form.password, hashed_password=existing_obj.password):
            logger.warning(f"用户 {login_form.username} 密码错误")
            raise ValueError(f"用户 {login_form.username} 密码错误")
        
        access_expires: timedelta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token: str = create_access_token(
            payload=JWTPayloadSchema(
                sub=existing_obj.username,
                exp=datetime.now() + access_expires,
            )
        )
        logger.info(f"用户{existing_obj.username}登录成功")
        
        return JWTOutSchema(
            access_token=access_token,
            token_type=settings.TOKEN_TYPE,
            expires_in=access_expires.total_seconds()
        )

    @classmethod
    def logout(cls, db: Session, user: User) -> None:
        """用户登出处理"""
        if not user.status:
            logger.warning(f"用户{user.username}已禁用")
            raise ValueError(f"用户{user.username}已禁用")
        
        logger.info(f"{user.username} 用户退出登录成功")

    @classmethod
    def user_list(cls, db: Session, query: UserQuerySchema, params: Params) -> Page[User]:
        """获取用户列表"""
        # 构建查询
        sql = select(User)
        if query.name:
            sql = sql.where(User.name.contains(query.name))
        sql = sql.order_by(asc(User.id))

        logger.info(f"查询用户列表，参数: {query}")
        return paginate(db, sql, params)

    @classmethod
    def user_detail(cls, db: Session, user_id: int) -> User:
        """获取用户详情"""
        existing_obj: User | None = db.exec(select(User).where(User.id == user_id)).first()
        if not existing_obj:
            logger.warning(f"用户ID {user_id} 不存在")
            raise ValueError(f"用户ID {user_id} 不存在")
        
        logger.info(f"获取用户{existing_obj.username}详情成功")
        return existing_obj

    @classmethod
    def user_create(cls, db: Session, data: UserInSchema) -> User:
        """创建用户"""
        existing_obj: User | None = db.exec(
            select(User).where(User.username == data.username)
        ).first()
        if existing_obj:
            logger.warning(f"用户{data.username}已存在")
            raise ValueError(f"用户{data.username}已存在")

        # 创建用户
        new_obj: User = User(**data.model_dump())
        new_obj.password = set_password_hash(data.password)
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)

        logger.info(f"创建用户{new_obj.username}成功")
        return new_obj

    @classmethod
    def user_update(cls, db: Session, user_id: int, data: UserInSchema) -> User:
        """更新用户信息"""
        existing_obj: User | None = db.exec(select(User).where(User.id == user_id)).first()
        if not existing_obj:
            logger.warning(f"用户ID {user_id} 不存在")
            raise ValueError(f"用户ID {user_id} 不存在")

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
                raise ValueError(f"用户名{update_data['username']}已存在")

        # 更新用户信息
        for key, value in update_data.items():
            setattr(existing_obj, key, value)

        db.commit()
        db.refresh(existing_obj)

        logger.info(f"更新用户{existing_obj.username}成功")
        return existing_obj

    @classmethod
    def user_delete(cls, db: Session, user_id: int) -> User:
        """删除用户"""
        existing_obj: User | None = db.exec(select(User).where(User.id == user_id)).first()
        if not existing_obj:
            logger.warning(f"用户ID {user_id} 不存在")
            raise ValueError(f"用户ID {user_id} 不存在")

        # 删除用户
        db.delete(existing_obj)
        db.commit()

        logger.info(f"删除用户{existing_obj.username}成功")
        return existing_obj
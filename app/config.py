# -*- coding: utf-8 -*-

"""
统一配置管理模块
提供一致的配置管理接口，支持环境变量和配置文件
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    SQLITE_DB_NAME: str = "app.db"
    DB_ECHO: bool = Field(default=False, description="是否打印SQL语句")
    BASE_DIR: Path = Field(default=Path("/"), description="项目根目录")  # 由主配置类设置


class JWTConfig(BaseSettings):
    """JWT配置"""
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT密钥，生产环境必须修改")
    ALGORITHM: str = Field(default="HS256", description="JWT算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间(分钟)")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="刷新令牌过期时间(分钟)")
    TOKEN_TYPE: str = Field(default="bearer", description="令牌类型")


class ServiceDiscoveryConfig(BaseSettings):
    """服务发现配置"""
    CONSUL_HOST: str = Field(default="localhost", description="Consul主机地址")
    CONSUL_PORT: int = Field(default=8500, description="Consul端口")
    CONSUL_TIMEOUT: float = Field(default=10.0, description="Consul请求超时时间")
    SERVICE_CACHE_TTL: int = Field(default=30, description="服务缓存有效期(秒)")


class SecurityConfig(BaseSettings):
    """安全配置"""
    CORS_ORIGINS: List[str] = Field(default=["*"], description="允许的CORS来源")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="是否允许CORS凭证")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], description="允许的CORS方法")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], description="允许的CORS头")
    ENABLE_GZIP: bool = Field(default=True, description="是否启用GZIP压缩")
    GZIP_COMPRESSION_LEVEL: int = Field(default=6, description="GZIP压缩级别(1-9)")
    SECURE_HEADERS: bool = Field(default=True, description="是否启用安全HTTP头部")
    TRUSTED_HOSTS: List[str] = Field(default=["*"], description="受信任的主机列表")
    ENABLE_X_FRAME_OPTIONS: bool = Field(default=True, description="是否启用X-Frame-Options头")
    ENABLE_CONTENT_SECURITY_POLICY: bool = Field(default=False, description="是否启用Content-Security-Policy头")
    CONTENT_SECURITY_POLICY: str = Field(default="default-src 'self'", description="内容安全策略")


class ServiceConfig(BaseSettings):
    """服务配置"""
    SERVICE_NAME: str = Field(default="fastapi-service", description="服务名称")
    API_VERSION: str = Field(default="1.0.0", description="API版本")
    API_V1_STR: str = Field(default="/api/v1", description="API v1前缀")
    SERVICE_PORT: int = Field(default=8000, description="服务端口")
    SERVICE_HOST: str = Field(default="0.0.0.0", description="服务监听地址")


class LoggingConfig(BaseSettings):
    """日志配置"""
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_DIR: Path = Field(default=Path("logs"), description="日志目录")
    LOG_MAX_BYTES: int = Field(default=10*1024*1024, description="单个日志文件最大字节数")
    LOG_BACKUP_COUNT: int = Field(default=5, description="日志文件备份数量")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="日志格式")


class Settings(BaseSettings):
    """主配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",  # 支持嵌套环境变量，如 DB__HOST=localhost
        extra="ignore",  # 忽略未知的环境变量
    )
    
    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent

    # 基础配置
    DEBUG: bool = Field(default=False, description="是否开启调试模式")
    ENVIRONMENT: str = Field(default="development", description="环境: development, production, testing")
    
    # 嵌套配置
    db: DatabaseSettings = DatabaseSettings()
    jwt: JWTConfig = JWTConfig()
    service: ServiceConfig = ServiceConfig()
    discovery: ServiceDiscoveryConfig = ServiceDiscoveryConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()


@lru_cache(maxsize=1)
def get_settings(**kwargs) -> Settings:
    """
    获取通用配置实例（带缓存）
    
    Args:
        **kwargs: 额外的配置参数
        
    Returns:
        Settings: 配置实例
    """
    return Settings(**kwargs)


# 默认配置实例
settings = get_settings()
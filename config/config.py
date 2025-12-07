# -*- coding: utf-8 -*-

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """主配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent

    # 基础配置
    DEBUG: bool = True
    
    SERVICE_NAME: str = "fastapi-service"
    SERVICE_VERSION: str = "v1"
    SERVICE_SUMMARY: str = "FastAPI服务"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8000
    SERVICE_DESCRIPTION: str = "FastAPI服务"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    TOKEN_TYPE: str = "bearer"

    SQLITE_DB_NAME: str = "sqlite.db"

    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"


@lru_cache(maxsize=16)
def get_settings(**kwargs) -> Settings:
    return Settings(**kwargs)

# 提供向后兼容的settings变量
settings = get_settings()
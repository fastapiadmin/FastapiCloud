#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from app.config import settings
from core.logger import logger, setup_logging
from core.middlewares import register_middleware_handler
from core.exceptions import register_exception_handlers
from core.discovery import ServiceDiscoveryClient

from services.admin.app.api.user import router
from core.health import router as health_router


# 服务发现实例
service_discovery = ServiceDiscoveryClient(
    consul_host=settings.discovery.CONSUL_HOST,
    consul_port=settings.discovery.CONSUL_PORT,
    timeout=settings.discovery.CONSUL_TIMEOUT,
    cache_ttl=settings.discovery.SERVICE_CACHE_TTL
)

# 初始化日志配置
setup_logging(log_dir=settings.logging.LOG_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    自定义生命周期
    """
    try:
        logger.info(f"用户服务启动...{app.title}")
        from core.database import create_db_and_tables
        await create_db_and_tables()

        # 注册服务到Consul
        service_id = f"{settings.service.SERVICE_NAME}-{uuid.uuid4()}"
        service_address = os.getenv("HOST", "localhost")
        service_port = settings.service.SERVICE_PORT
        
        # 健康检查配置
        check = {
            "HTTP": f"http://{service_address}:{service_port}/health",
            "Interval": "10s",
            "Timeout": "5s"
        }

        # 注册服务
        await service_discovery.register_service(
            service_name=settings.service.SERVICE_NAME,
            service_id=service_id,
            address=service_address,
            port=service_port,
            tags=[settings.service.API_VERSION, "user-service", "auth"],
            check=check
        )
        logger.info(f"服务注册成功: {settings.service.SERVICE_NAME} (ID: {service_id})")

        yield
    except Exception as e:
        logger.error(f"用户服务启动失败: {e}")
        raise e
    finally:
        logger.info(f"用户服务关闭...{app.title}")


def create_app() -> FastAPI:
    # 创建FastAPI应用
    app: FastAPI = FastAPI(
        lifespan=lifespan, 
        debug=settings.DEBUG, 
        title=settings.service.SERVICE_NAME,
        version=settings.service.API_VERSION,
        description="用户管理微服务"
    )
    # 注册中间件
    register_middleware_handler(app)
    # 注册异常处理器
    register_exception_handlers(app)
    # 注册分页插件
    add_pagination(app)
    # 注册路由
    app.include_router(router=router, prefix=settings.service.API_V1_STR)
    # 注册健康检查和监控路由
    app.include_router(router=health_router)
    # 挂载静态文件
    app.mount(path="/static", app=StaticFiles(directory="static"), name="static")
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:create_app", host=settings.service.SERVICE_HOST, port=settings.service.SERVICE_PORT, reload=settings.DEBUG, log_config=None)


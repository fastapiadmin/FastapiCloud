#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import asynccontextmanager
from collections.abc import AsyncGenerator
import uvicorn
import uuid

from app.config import settings
from core.logger import logger, setup_logging
from core.middlewares import register_middleware_handler
from core.exceptions import register_exception_handlers
from core.discovery import ServiceDiscoveryClient
from app.router import gateway

# 初始化日志配置
setup_logging(log_dir=settings.BASE_DIR.joinpath("services/api-gateway/logs"))

# 创建服务发现实例
service_discovery = ServiceDiscoveryClient(
    consul_host=settings.discovery.CONSUL_HOST,
    consul_port=settings.discovery.CONSUL_PORT
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    应用程序生命周期管理
    """
    # 启动事件
    logger.info("API Gateway 启动中...")
    logger.info(f"服务名称: {settings.service.SERVICE_NAME}")
    logger.info(f"API版本: {settings.service.API_VERSION}")
    logger.info(f"服务地址: http://localhost:{settings.service.SERVICE_PORT}")
    
    # 注册服务到Consul
    service_id = f"{settings.service.SERVICE_NAME}-{uuid.uuid4()}"
    service_address = "localhost"
    service_port = settings.service.SERVICE_PORT
    
    await service_discovery.register_service(
        service_name=settings.service.SERVICE_NAME,
        service_id=service_id,
        address=service_address,
        port=service_port,
        tags=["api-gateway", "v1"],
        check={
            "HTTP": f"http://{service_address}:{service_port}/health",
            "Interval": "10s",
            "Timeout": "5s"
        }
    )
    
    
    try:
        yield
    except Exception as e:
        logger.error(f"API网关运行异常: {e}")
        raise e
    finally:
        # 关闭事件
        await service_discovery.deregister_service(service_id=service_id)
        logger.info("API Gateway 关闭中...")


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    """
    app = FastAPI(
        title=settings.service.SERVICE_NAME,
        version=settings.service.API_VERSION,
        description="API Gateway for FastAPI Microservices",
        lifespan=lifespan
    )
    
    # 注册中间件
    register_middleware_handler(app)
    
    # 注册异常处理器
    register_exception_handlers(app)
    
    # 注册路由
    app.include_router(gateway, tags=["网关系统"], prefix=settings.service.API_V1_STR)
    
    # 挂载静态文件目录
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app


if __name__ == "__main__":
    uvicorn.run(
        "main:create_app",
        host=settings.service.SERVICE_HOST,
        port=settings.service.SERVICE_PORT,
        reload=True,
        log_config=None  # 禁用uvicorn默认日志配置，使用自定义日志
    )

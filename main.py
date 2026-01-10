#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typer
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi.concurrency import asynccontextmanager
from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.core.logger import logger, setup_logging
from app.core.middlewares import register_middleware_handler
from app.core.exceptions import register_exception_handlers
from app.api.router import admin

cli = typer.Typer()
# 初始化 Alembic 配置
alembic_cfg: Config = Config(file_="alembic.ini")
# 初始化日志配置
setup_logging(log_dir=settings.LOG_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    自定义生命周期
    """
    try:
        logger.info(f"服务启动...{app.title}")
        from app.core.database import create_db_and_tables
        await create_db_and_tables()

        yield
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise e
    finally:
        logger.info(f"服务关闭...{app.title}")

def create_app() -> FastAPI:
    # 创建FastAPI应用
    app = FastAPI(
        debug=settings.DEBUG, 
        lifespan=lifespan, 
        title=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        summary=settings.SERVICE_SUMMARY,
        description=settings.SERVICE_DESCRIPTION
    )
    # 注册中间件
    register_middleware_handler(app)
    # 注册异常处理器
    register_exception_handlers(app)
    # 注册分页插件
    add_pagination(app)
    # 注册路由
    app.include_router(router=admin)
    # 先挂载根目录的静态文件，这样可以直接访问/favicon.ico、/logo.svg等
    app.mount(path="/", app=StaticFiles(directory=settings.BASE_DIR.joinpath("static")), name="static_root")
    # 处理所有路径请求，返回index.html（用于SPA路由）
    # 这个路由会在静态文件挂载之后检查，所以存在的静态文件会优先被返回
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        from fastapi.responses import FileResponse
        return FileResponse(settings.BASE_DIR.joinpath("static/index.html"))
    return app

@cli.command()
def migrate(message: str | None = "生成新的 Alembic 迁移脚本") -> None:
    """
    生成新的 Alembic 迁移脚本。/应用最新的 Alembic 迁移。
    """
    command.revision(config=alembic_cfg, message=message, autogenerate=True)
    typer.echo(message=f"生成新的 Alembic 迁移脚本")
    command.upgrade(config=alembic_cfg, revision="head")
    typer.echo(message="所有迁移已应用。")

@cli.command()
def run() -> None:
    """
    启动应用。
    """
    import uvicorn
    uvicorn.run(
        app="main:create_app", 
        host=settings.SERVICE_HOST, 
        port=settings.SERVICE_PORT, 
        reload=settings.DEBUG, # 开发模式下自动重载
        factory=True,
        log_config=None
    )

if __name__ == "__main__":
    cli()


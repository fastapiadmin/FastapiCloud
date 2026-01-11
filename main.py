#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typer
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi.concurrency import asynccontextmanager
from alembic import command
from alembic.config import Config

from core.config import settings
from core.logger import logger, setup_logging
from core.middlewares import register_middleware_handler
from core.exceptions import register_exception_handlers
from core.plugins import PluginManager, PluginContext
from apps.api.router import admin

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
        from core.database import create_db_and_tables
        await create_db_and_tables()
        
        # 加载插件
        plugin_context = PluginContext(app=app, settings=settings, logger=logger)
        app.state.plugin_manager = PluginManager(plugin_context)
        await app.state.plugin_manager.load_all_plugins()
        
        yield
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise e
    finally:
        # 卸载插件
        if hasattr(app.state, "plugin_manager"):
            await app.state.plugin_manager.unload_all_plugins()
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
    
    # 尝试直接导入demo_router，这样FastAPI就能在启动时发现路由了
    try:
        from plugins.demo_plugin.demo_plugin import demo_router
        app.include_router(demo_router)
        logger.info(f"已直接注册demo_router: {demo_router.prefix}")
    except ImportError as e:
        logger.warning(f"无法导入demo_router: {e}")
    except Exception as e:
        logger.error(f"注册demo_router时出错: {e}")
    # 先挂载根目录的静态文件，这样可以直接访问/favicon.ico、/logo.svg等
    app.mount(path="/", app=StaticFiles(directory=settings.BASE_DIR.joinpath("static")), name="static")
    
    # 调试端点，用于查看所有注册的路由
    @app.get("/debug/routes")
    async def get_all_routes(request: Request):
        routes = []
        for route in request.app.routes:
            if hasattr(route, "path"):
                routes.append({
                    "path": route.path,
                    "name": route.name,
                    "methods": list(route.methods) if hasattr(route, "methods") else []
                })
        return JSONResponse({
            "status": "success",
            "routes": routes
        })
    
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


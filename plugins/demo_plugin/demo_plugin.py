# -*- coding: utf-8 -*-
"""
演示插件示例
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core.plugins import BasePlugin, PluginInfo, PluginContext


# 在文件顶部定义路由，这样FastAPI可以在启动时扫描到它们
demo_router = APIRouter(prefix="/api/plugin/demo", tags=["演示插件"])


@demo_router.get("/info")
async def get_plugin_info(request: Request) -> JSONResponse:
    """获取插件信息"""
    plugin_manager = request.app.state.plugin_manager
    plugins = plugin_manager.list_plugins()
    
    # 获取所有注册的路由
    routes = []
    for route in request.app.routes:
        if hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, "methods") else []
            })
    
    return JSONResponse(
        {
            "status": "success",
            "message": "演示插件 API",
            "plugins": [plugin.model_dump() for plugin in plugins],
            "routes": routes
        }
    )


@demo_router.get("/hello")
async def hello_world() -> JSONResponse:
    """简单的Hello World接口"""
    return JSONResponse({
        "message": "Hello from Demo Plugin!"
    })


class DemoPlugin(BasePlugin):
    """演示插件"""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="demo_plugin",
            version="1.0.0",
            author="FastAPI Cloud",
            description="这是一个演示插件，展示如何使用插件系统",
            enabled=True
        )
    
    async def on_startup(self) -> None:
        """插件启动时调用"""
        self.logger.info(f"演示插件 {self.info.name} v{self.info.version} 已启动")
        # 路由已经在main.py中注册，这里不需要再注册了
    
    async def on_shutdown(self) -> None:
        """插件关闭时调用"""
        self.logger.info(f"演示插件 {self.info.name} v{self.info.version} 已关闭")

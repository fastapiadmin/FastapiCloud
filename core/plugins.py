# -*- coding: utf-8 -*-
"""
插件系统核心模块

定义插件接口和生命周期管理
"""

import sys
from typing import Dict, List, Optional, TypeVar, Generic, Any
from fastapi import FastAPI
from abc import ABC, abstractmethod
from pydantic import BaseModel
import importlib
import os
import pkgutil


class PluginInfo(BaseModel):
    """插件信息"""
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True


class PluginContext(BaseModel):
    """插件上下文信息"""
    app: FastAPI
    settings: Any
    logger: Any
    
    model_config = {
        "arbitrary_types_allowed": True
    }


T = TypeVar('T', bound='BasePlugin')


class BasePlugin(ABC, Generic[T]):
    """插件基类，所有插件必须继承此类"""
    
    def __init__(self, context: PluginContext):
        self.context = context
        self.app = context.app
        self.settings = context.settings
        self.logger = context.logger
        
    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    @abstractmethod
    async def on_startup(self) -> None:
        """插件启动时调用"""
        pass
    
    @abstractmethod
    async def on_shutdown(self) -> None:
        """插件关闭时调用"""
        pass
    
    def register_router(self, router) -> None:
        """注册路由"""
        if hasattr(self, 'app') and self.app is not None:
            self.logger.info(f"正在注册路由: {router.prefix}，包含 {len(router.routes)} 个路由")
            self.app.include_router(router)
            # 检查路由是否真的被注册到了应用程序
            for route in router.routes:
                if hasattr(route, "path"):
                    self.logger.info(f"已注册路由: {route.path}")
        else:
            self.logger.error("无法注册路由: 应用程序实例未找到")
    
    def register_middleware(self, middleware_cls, **kwargs) -> None:
        """注册中间件"""
        self.app.add_middleware(middleware_cls, **kwargs)
    
    def register_event_handler(self, event_type: str, handler) -> None:
        """注册事件处理器"""
        if event_type == "startup":
            self.app.add_event_handler("startup", handler)
        elif event_type == "shutdown":
            self.app.add_event_handler("shutdown", handler)


class PluginManager:
    """插件管理器"""
    
    def __init__(self, context: PluginContext):
        self.context = context
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
        
        # 确保插件目录存在
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
    
    def discover_plugins(self) -> List[str]:
        """发现所有插件"""
        plugins = []
        
        # 添加插件目录到Python路径
        if self.plugins_dir not in sys.path:
            sys.path.append(self.plugins_dir)
        
        # 遍历插件目录
        for _, name, ispkg in pkgutil.iter_modules([self.plugins_dir]):
            if ispkg:
                plugins.append(name)
        
        return plugins
    
    async def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """加载单个插件"""
        try:
            # 导入插件模块
            plugin_module = importlib.import_module(plugin_name)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(plugin_module):
                attr = getattr(plugin_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugin_class = attr
                    break
            
            if not plugin_class:
                self.context.logger.error(f"插件 {plugin_name} 中未找到继承自 BasePlugin 的类")
                return None
            
            # 初始化插件
            plugin = plugin_class(self.context)
            
            # 检查插件信息
            if not plugin.info.name:
                self.context.logger.error(f"插件 {plugin_name} 未设置名称")
                return None
            
            # 如果插件已启用，启动插件
            if plugin.info.enabled:
                await plugin.on_startup()
                self.plugins[plugin.info.name] = plugin
                self.context.logger.info(f"成功加载插件: {plugin.info.name} v{plugin.info.version}")
            
            return plugin
            
        except Exception as e:
            self.context.logger.error(f"加载插件 {plugin_name} 失败: {str(e)}", exc_info=True)
            return None
    
    async def load_all_plugins(self) -> None:
        """加载所有插件"""
        self.context.logger.info("开始发现和加载插件...")
        
        plugins = self.discover_plugins()
        
        if not plugins:
            self.context.logger.info("未发现任何插件")
            return
        
        for plugin_name in plugins:
            await self.load_plugin(plugin_name)
        
        self.context.logger.info(f"插件加载完成，共加载 {len(self.plugins)} 个插件")
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """卸载单个插件"""
        try:
            if plugin_name not in self.plugins:
                self.context.logger.error(f"插件 {plugin_name} 未加载")
                return False
            
            plugin = self.plugins[plugin_name]
            await plugin.on_shutdown()
            del self.plugins[plugin_name]
            self.context.logger.info(f"成功卸载插件: {plugin_name}")
            return True
            
        except Exception as e:
            self.context.logger.error(f"卸载插件 {plugin_name} 失败: {str(e)}", exc_info=True)
            return False
    
    async def unload_all_plugins(self) -> None:
        """卸载所有插件"""
        self.context.logger.info("开始卸载所有插件...")
        
        for plugin_name in list(self.plugins.keys()):
            await self.unload_plugin(plugin_name)
        
        self.context.logger.info("所有插件已卸载")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """获取所有插件信息"""
        return [plugin.info for plugin in self.plugins.values()]

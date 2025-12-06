# -*- coding: utf-8 -*-

"""
统一HTTP客户端模块
用于服务间通信的统一HTTP客户端实现
"""

import httpx
import asyncio
import random
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
from .logger import logger
from app.config import settings


class HttpClient:
    """统一HTTP客户端类"""
    
    def __init__(self, 
                 timeout: float = 30.0, 
                 retries: int = 3,
                 follow_redirects: bool = True,
                 headers: Optional[Dict[str, str]] = None,
                 max_connections: int = 100):
        """
        初始化HTTP客户端
        
        Args:
            timeout: 请求超时时间（秒）
            retries: 重试次数
            follow_redirects: 是否跟随重定向
            headers: 默认请求头
            max_connections: 最大连接数
        """
        self.timeout: float = timeout
        self.retries: int = retries
        self.follow_redirects: bool = follow_redirects
        self.headers: Dict[str, str] = headers or {}
        
        # 配置HTTP客户端
        limits = httpx.Limits(max_connections=max_connections)
        self.client: httpx.AsyncClient = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=follow_redirects,
            headers=headers,
            limits=limits
        )
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    def add_header(self, name: str, value: str):
        """
        添加默认请求头
        
        Args:
            name: 头名称
            value: 头值
        """
        self.headers[name] = value
        self.client.headers[name] = value
    
    def remove_header(self, name: str):
        """
        移除默认请求头
        
        Args:
            name: 头名称
        """
        if name in self.headers:
            del self.headers[name]
        if name in self.client.headers:
            del self.client.headers[name]
    
    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        带重试机制的HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        last_exception = None
        
        for attempt in range(self.retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                # 如果是5xx错误或连接错误，进行重试
                if (response.status_code >= 500 or response.status_code == 429) and attempt < self.retries:
                    retry_after = response.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else (0.1 * (2 ** attempt))
                    
                    logger.warning(f"服务返回{response.status_code}错误，第{attempt + 1}次重试: {url}, 等待{sleep_time}秒")
                    await asyncio.sleep(sleep_time)  # 退避策略
                    continue
                return response
            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.retries:
                    logger.warning(f"请求失败，第{attempt + 1}次重试: {url}, 错误: {e}")
                    await asyncio.sleep(0.1 * (2 ** attempt))  # 指数退避
                    continue
                else:
                    logger.error(f"请求最终失败: {url}, 错误: {e}")
                    raise
        
        # 如果所有重试都失败了
        if last_exception is not None:
            raise last_exception
        else:
            raise RuntimeError("请求失败且未捕获到具体异常")
    
    async def get(self, url: str, params=None, headers=None) -> httpx.Response:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: 查询参数
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("GET", url, params=params, headers=headers)
    
    async def post(self, url: str, data=None, json=None, headers=None) -> httpx.Response:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("POST", url, content=data, json=json, headers=headers)
    
    async def put(self, url: str, data=None, json=None, headers=None) -> httpx.Response:
        """
        发送PUT请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("PUT", url, content=data, json=json, headers=headers)
    
    async def patch(self, url: str, data=None, json=None, headers=None) -> httpx.Response:
        """
        发送PATCH请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("PATCH", url, content=data, json=json, headers=headers)
    
    async def delete(self, url: str, headers=None) -> httpx.Response:
        """
        发送DELETE请求
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("DELETE", url, headers=headers)


# 全局HTTP客户端实例
_http_client = None


async def get_http_client() -> HttpClient:
    """
    获取HTTP客户端实例
    
    Returns:
        HttpClient: HTTP客户端实例
    """
    global _http_client
    if _http_client is None:
        _http_client = HttpClient()
    return _http_client


async def close_http_client() -> None:
    """
    关闭HTTP客户端
    """
    global _http_client
    if _http_client is not None:
        await _http_client.close()
        _http_client = None


class ServiceClient:
    """
    服务间通信客户端
    与服务发现集成，简化服务间调用
    """
    
    def __init__(self, 
                 service_name: str, 
                 http_client: HttpClient,
                 service_discovery):
        """
        初始化服务间通信客户端
        
        Args:
            service_name: 目标服务名称
            http_client: HTTP客户端实例
            service_discovery: 服务发现客户端实例
        """
        self.service_name = service_name
        self.http_client = http_client
        self.service_discovery = service_discovery
        self.service_instances = []
        self.last_discovered = 0
    
    async def init(self):
        """
        初始化客户端
        """
        if not self.http_client:
            self.http_client = await get_http_client()
        
        if not self.service_discovery:
            from .discovery import get_service_discovery_client
            self.service_discovery = await get_service_discovery_client()
    
    async def _discover_service(self):
        """
        发现服务实例
        """
        self.service_instances = await self.service_discovery.discover_service(self.service_name)
        if not self.service_instances:
            raise RuntimeError(f"未找到服务实例: {self.service_name}")
    
    async def _get_service_url(self, path: str) -> str:
        """
        获取服务实例URL
        
        Args:
            path: 请求路径
            
        Returns:
            完整的服务URL
        """
        # 如果没有服务实例或超过缓存时间，重新发现
        if not self.service_instances:
            await self._discover_service()
        
        # 随机选择一个服务实例（简单负载均衡）
        instance = random.choice(self.service_instances)
        base_url = f"http://{instance.address}:{instance.port}"
        return urljoin(base_url, path)
    
    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """
        发送请求到目标服务
        
        Args:
            method: HTTP方法
            path: 请求路径
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        if not self.http_client or not self.service_discovery:
            await self.init()
        
        url = await self._get_service_url(path)
        return await self.http_client._request_with_retry(method, url, **kwargs)
    
    async def get(self, path: str, **kwargs) -> httpx.Response:
        """
        发送GET请求到目标服务
        
        Args:
            path: 请求路径
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        return await self.request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> httpx.Response:
        """
        发送POST请求到目标服务
        
        Args:
            path: 请求路径
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        return await self.request("POST", path, **kwargs)
    
    async def put(self, path: str, **kwargs) -> httpx.Response:
        """
        发送PUT请求到目标服务
        
        Args:
            path: 请求路径
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        return await self.request("PUT", path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """
        发送DELETE请求到目标服务
        
        Args:
            path: 请求路径
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        return await self.request("DELETE", path, **kwargs)


__all__ = [
    "HttpClient",
    "get_http_client",
    "close_http_client",
    "ServiceClient"
]
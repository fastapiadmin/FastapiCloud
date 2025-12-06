# -*- coding: utf-8 -*-

"""
统一服务发现与健康检查模块
提供一致的服务注册、发现和健康检查机制
"""

import asyncio
import httpx
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import uuid

from .logger import logger
from app.config import settings


class ServiceInstance:
    """服务实例信息"""
    
    def __init__(
        self,
        service_id: str,
        service_name: str,
        address: str,
        port: int,
        tags: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        """
        初始化服务实例
        
        Args:
            service_id: 服务ID
            service_name: 服务名称
            address: 服务地址
            port: 服务端口
            tags: 服务标签
            meta: 服务元数据
        """
        self.service_id = service_id
        self.service_name = service_name
        self.address = address
        self.port = port
        self.tags = tags or []
        self.meta = meta or {}
        self.healthy = True
        self.last_check_time = None


class ServiceDiscoveryClient:
    """服务发现客户端"""
    
    def __init__(
        self,
        consul_host: str = "localhost",
        consul_port: int = 8500,
        timeout: float = 10.0,
        cache_ttl: int = 30
    ):
        """
        初始化服务发现客户端
        
        Args:
            consul_host: Consul主机地址
            consul_port: Consul端口
            timeout: 请求超时时间
            cache_ttl: 服务缓存有效期（秒）
        """
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.base_url = f"http://{consul_host}:{consul_port}/v1"
        self.timeout = timeout
        self.http_client = httpx.AsyncClient(timeout=timeout)
        self.services_cache: Dict[str, List[ServiceInstance]] = {}
        self.cache_ttl = cache_ttl  # 缓存有效期（秒）
        self.last_cache_update = {}
    
    async def register_service(
        self,
        service_name: str,
        service_id: Optional[str] = None,
        address: str = "localhost",
        port: int = 8000,
        tags: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        check: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        注册服务
        
        Args:
            service_name: 服务名称
            service_id: 服务ID
            address: 服务地址
            port: 服务端口
            tags: 服务标签
            meta: 服务元数据
            check: 健康检查配置
            
        Returns:
            bool: 注册是否成功
        """
        try:
            if not service_id:
                service_id = f"{service_name}-{uuid.uuid4()}"
            
            # 构建注册数据
            registration_data = {
                "ID": service_id,
                "Name": service_name,
                "Address": address,
                "Port": port,
                "Tags": tags or [],
                "Meta": meta or {}
            }
            
            # 添加健康检查配置
            if check:
                registration_data["Check"] = check
            else:
                # 默认健康检查配置
                registration_data["Check"] = {
                    "HTTP": f"http://{address}:{port}/health",
                    "Interval": "10s",
                    "Timeout": "5s",
                    "DeregisterCriticalServiceAfter": "1m"
                }
            
            # 发送注册请求
            response = await self.http_client.put(
                f"{self.base_url}/agent/service/register",
                json=registration_data
            )
            
            if response.status_code == 200:
                logger.info(f"服务注册成功: {service_name} ({service_id})")
                return True
            else:
                logger.error(f"服务注册失败: {service_name}, 状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"服务注册异常: {service_name}, 错误: {str(e)}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """
        注销服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 注销是否成功
        """
        try:
            response = await self.http_client.put(
                f"{self.base_url}/agent/service/deregister/{service_id}"
            )
            
            if response.status_code == 200:
                logger.info(f"服务注销成功: {service_id}")
                # 清除缓存
                self._clear_service_cache()
                return True
            else:
                logger.error(f"服务注销失败: {service_id}, 状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"服务注销异常: {service_id}, 错误: {str(e)}")
            return False
    
    async def discover_service(self, service_name: str) -> List[ServiceInstance]:
        """
        发现服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            List[ServiceInstance]: 服务实例列表
        """
        try:
            # 检查缓存
            if self._is_cache_valid(service_name):
                return self.services_cache.get(service_name, [])
            
            # 从Consul获取服务实例
            response = await self.http_client.get(
                f"{self.base_url}/health/service/{service_name}",
                params={"passing": "true"}  # 只获取健康的实例
            )
            
            if response.status_code == 200:
                services_data = response.json()
                service_instances = []
                
                for service_data in services_data:
                    service_info = service_data.get("Service", {})
                    service_instance = ServiceInstance(
                        service_id=service_info.get("ID"),
                        service_name=service_info.get("Service"),
                        address=service_info.get("Address"),
                        port=service_info.get("Port"),
                        tags=service_info.get("Tags", []),
                        meta=service_info.get("Meta", {})
                    )
                    service_instances.append(service_instance)
                
                # 更新缓存
                self.services_cache[service_name] = service_instances
                self.last_cache_update[service_name] = asyncio.get_event_loop().time()
                
                logger.info(f"服务发现成功: {service_name}, 实例数: {len(service_instances)}")
                return service_instances
            else:
                logger.error(f"服务发现失败: {service_name}, 状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"服务发现异常: {service_name}, 错误: {str(e)}")
            return []
    
    async def get_all_services(self) -> Dict[str, List[str]]:
        """
        获取所有服务
        
        Returns:
            Dict[str, List[str]]: 服务名称和标签映射
        """
        try:
            response = await self.http_client.get(f"{self.base_url}/catalog/services")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取所有服务失败, 状态码: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"获取所有服务异常, 错误: {str(e)}")
            return {}
    
    async def check_service_health(self, service_id: str) -> bool:
        """
        检查服务健康状态
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 服务是否健康
        """
        try:
            response = await self.http_client.get(
                f"{self.base_url}/health/checks/{service_id}"
            )
            
            if response.status_code == 200:
                checks = response.json()
                # 检查所有检查项是否通过
                for check in checks:
                    if check.get("Status") != "passing":
                        return False
                return True
            else:
                logger.error(f"健康检查失败: {service_id}, 状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"健康检查异常: {service_id}, 错误: {str(e)}")
            return False
    
    def _is_cache_valid(self, service_name: str) -> bool:
        """
        检查缓存是否有效
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 缓存是否有效
        """
        if service_name not in self.last_cache_update:
            return False
        
        last_update = self.last_cache_update[service_name]
        current_time = asyncio.get_event_loop().time()
        return (current_time - last_update) < self.cache_ttl
    
    def _clear_service_cache(self) -> None:
        """清除服务缓存"""
        self.services_cache.clear()
        self.last_cache_update.clear()
    
    async def close(self) -> None:
        """关闭客户端"""
        await self.http_client.aclose()


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, discovery_client: ServiceDiscoveryClient):
        """
        初始化健康检查器
        
        Args:
            discovery_client: 服务发现客户端
        """
        self.discovery_client = discovery_client
        self.http_client = httpx.AsyncClient(timeout=5.0)
        self.healthy_services: set = set()
        self.unhealthy_services: set = set()
    
    async def check_service_endpoint(self, endpoint: str) -> bool:
        """
        检查服务端点健康状态
        
        Args:
            endpoint: 服务端点URL
            
        Returns:
            bool: 端点是否健康
        """
        try:
            # 确保URL包含健康检查路径
            if not endpoint.endswith("/health"):
                parsed_url = urlparse(endpoint)
                if parsed_url.path == "" or parsed_url.path == "/":
                    endpoint = endpoint.rstrip("/") + "/health"
            
            response = await self.http_client.get(endpoint, timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"健康检查失败: {endpoint}, 错误: {str(e)}")
            return False
    
    async def check_all_services(self) -> Dict[str, bool]:
        """
        检查所有服务的健康状态
        
        Returns:
            Dict[str, bool]: 服务健康状态映射
        """
        try:
            all_services = await self.discovery_client.get_all_services()
            health_status = {}
            
            for service_name in all_services.keys():
                service_instances = await self.discovery_client.discover_service(service_name)
                
                if service_instances:
                    # 检查第一个实例的健康状态
                    instance = service_instances[0]
                    health_url = f"http://{instance.address}:{instance.port}/health"
                    is_healthy = await self.check_service_endpoint(health_url)
                    
                    health_status[service_name] = is_healthy
                    
                    if is_healthy:
                        self.healthy_services.add(service_name)
                        self.unhealthy_services.discard(service_name)
                    else:
                        self.unhealthy_services.add(service_name)
                        self.healthy_services.discard(service_name)
                else:
                    health_status[service_name] = False
                    self.unhealthy_services.add(service_name)
                    self.healthy_services.discard(service_name)
            
            return health_status
            
        except Exception as e:
            logger.error(f"批量健康检查异常: {str(e)}")
            return {}
    
    def is_service_healthy(self, service_name: str) -> bool:
        """
        检查服务是否健康
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否健康
        """
        return service_name in self.healthy_services
    
    async def close(self) -> None:
        """关闭健康检查器"""
        await self.http_client.aclose()


# 全局服务发现客户端实例
_discovery_client: Optional[ServiceDiscoveryClient] = None
_health_checker: Optional[HealthChecker] = None


async def get_service_discovery_client() -> ServiceDiscoveryClient:
    """
    获取服务发现客户端实例
    
    Returns:
        ServiceDiscoveryClient: 服务发现客户端实例
    """
    global _discovery_client
    if _discovery_client is None:
        _discovery_client = ServiceDiscoveryClient(
            consul_host=settings.discovery.CONSUL_HOST,
            consul_port=settings.discovery.CONSUL_PORT,
            timeout=settings.discovery.CONSUL_TIMEOUT,
            cache_ttl=settings.discovery.SERVICE_CACHE_TTL
        )
    return _discovery_client


async def get_health_checker() -> HealthChecker:
    """
    获取健康检查器实例
    
    Returns:
        HealthChecker: 健康检查器实例
    """
    global _health_checker
    if _health_checker is None:
        discovery_client = await get_service_discovery_client()
        _health_checker = HealthChecker(discovery_client)
    return _health_checker


async def close_service_discovery() -> None:
    """关闭服务发现相关资源"""
    global _discovery_client, _health_checker
    if _discovery_client:
        await _discovery_client.close()
        _discovery_client = None
    if _health_checker:
        await _health_checker.close()
        _health_checker = None


# 默认导出
__all__ = [
    "ServiceInstance",
    "ServiceDiscoveryClient",
    "HealthChecker",
    "get_service_discovery_client",
    "get_health_checker",
    "close_service_discovery"
]
#!/usr/bin/env python3
"""
P2P网络发现模块
"""

from zeroconf import ServiceInfo, Zeroconf
import socket
import threading
import json
from datetime import datetime

class P2PDiscovery:
    def __init__(self, device_id, device_name, port):
        """初始化P2P发现模块
        
        Args:
            device_id: 设备唯一标识
            device_name: 设备名称
            port: 服务端口
        """
        self.device_id = device_id
        self.device_name = device_name
        self.port = port
        self.zeroconf = Zeroconf()
        self.discovered_devices = {}
        self.service_info = None
        self.browser = None
        self.running = False
        
    def start(self):
        """启动服务发现"""
        self.running = True
        
        # 注册自己的服务
        local_ip = self._get_local_ip()
        self.service_info = ServiceInfo(
            type_="_file-sharing._tcp.local.",
            name=f"{self.device_name}._file-sharing._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=self.port,
            properties={"device_id": self.device_id, "name": self.device_name, "ip": local_ip, "port": str(self.port)}
        )
        self.zeroconf.register_service(self.service_info)
        
        # 开始发现其他服务
        from zeroconf import ServiceBrowser
        self.browser = ServiceBrowser(self.zeroconf, "_file-sharing._tcp.local.", self)
        
    def stop(self):
        """停止服务发现"""
        self.running = False
        if self.service_info:
            self.zeroconf.unregister_service(self.service_info)
        if self.zeroconf:
            self.zeroconf.close()
    
    def _get_local_ip(self):
        """获取本地IP地址"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    
    def add_service(self, zeroconf, type, name):
        """发现新服务"""
        info = zeroconf.get_service_info(type, name)
        if info:
            device_id = info.properties.get(b'device_id', b'').decode()
            device_name = info.properties.get(b'name', b'').decode()
            ip = socket.inet_ntoa(info.addresses[0])
            port = info.port
            if device_id != self.device_id:
                self.discovered_devices[device_id] = {
                    'name': device_name,
                    'ip': ip,
                    'port': port,
                    'last_seen': datetime.now().isoformat()
                }
                print(f"发现设备: {device_name} ({ip}:{port})")
    
    def remove_service(self, zeroconf, type, name):
        """服务消失"""
        info = zeroconf.get_service_info(type, name)
        if info:
            device_id = info.properties.get(b'device_id', b'').decode()
            if device_id in self.discovered_devices:
                del self.discovered_devices[device_id]
                print(f"设备离线: {device_id}")
    
    def get_discovered_devices(self):
        """获取发现的设备列表"""
        return self.discovered_devices
    
    def update_service(self, zeroconf, type, name):
        """服务更新"""
        # 当服务信息更新时调用
        pass

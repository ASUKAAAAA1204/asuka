#!/usr/bin/env python3
"""
P2P通信模块
"""

import socket
import threading
import json
import os
import struct
from datetime import datetime

class P2PServer:
    def __init__(self, host, port, file_manager, group_manager):
        """初始化P2P服务器
        
        Args:
            host: 服务器主机
            port: 服务器端口
            file_manager: 文件管理器
            group_manager: 组管理器
        """
        self.host = host
        self.port = port
        self.file_manager = file_manager
        self.group_manager = group_manager
        self.server_socket = None
        self.running = False
        self.threads = []
    
    def start(self):
        """启动服务器"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        thread = threading.Thread(target=self._accept_connections)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        print(f"P2P服务器启动在 {self.host}:{self.port}")
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1)
    
    def _accept_connections(self):
        """接受连接"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                thread = threading.Thread(target=self._handle_client, args=(client_socket, addr))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
            except Exception as e:
                if self.running:
                    print(f"接受连接出错: {e}")
                break
    
    def _handle_client(self, client_socket, addr):
        """处理客户端请求"""
        try:
            # 接收请求头长度
            header_length = client_socket.recv(4)
            if not header_length:
                return
            
            # 解析请求头
            header_size = struct.unpack('!I', header_length)[0]
            header_data = client_socket.recv(header_size)
            request = json.loads(header_data.decode())
            
            if request['type'] == 'file_request':
                # 处理文件请求
                file_id = request['file_id']
                group_id = request['group_id']
                file_info = self.file_manager.get_shared_file(file_id, group_id)
                if file_info:
                    # 发送文件
                    self._send_file(client_socket, file_info['file_path'])
                else:
                    # 发送错误
                    error_response = {'error': '文件不存在'}
                    self._send_response(client_socket, error_response)
            
            elif request['type'] == 'file_upload':
                # 处理文件上传
                file_name = request['filename']
                file_size = request['size']
                group_id = request['group_id']
                uploader_id = request['uploader_id']
                
                # 接收文件
                file_data = self._receive_file(client_socket, file_size)
                if file_data:
                    # 保存文件
                    save_path = self.file_manager.save_shared_file(file_name, file_data, group_id, uploader_id)
                    # 通知组内其他成员
                    self.group_manager.notify_group_members(group_id, 'file_added', {'file_id': save_path, 'filename': file_name})
                    # 发送成功响应
                    success_response = {'success': True, 'file_id': save_path}
                    self._send_response(client_socket, success_response)
                else:
                    # 发送错误
                    error_response = {'error': '文件接收失败'}
                    self._send_response(client_socket, error_response)
            
            elif request['type'] == 'group_invite':
                # 处理组邀请
                group_id = request['group_id']
                group_name = request['group_name']
                inviter_id = request['inviter_id']
                
                # 处理邀请逻辑
                result = self.group_manager.handle_group_invite(group_id, group_name, inviter_id)
                self._send_response(client_socket, result)
            
            elif request['type'] == 'file_change':
                # 处理文件变化通知
                group_id = request['group_id']
                file_path = request['file_path']
                change_type = request['change_type']
                
                # 处理文件变化
                self.file_manager.handle_file_change(group_id, file_path, change_type)
                self._send_response(client_socket, {'success': True})
                
        except Exception as e:
            print(f"处理客户端请求出错: {e}")
        finally:
            client_socket.close()
    
    def _send_file(self, client_socket, file_path):
        """发送文件"""
        try:
            # 发送文件大小
            file_size = os.path.getsize(file_path)
            client_socket.sendall(struct.pack('!I', file_size))
            
            # 发送文件数据
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
        except Exception as e:
            print(f"发送文件出错: {e}")
    
    def _receive_file(self, client_socket, file_size):
        """接收文件"""
        try:
            file_data = b''
            received = 0
            while received < file_size:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                file_data += chunk
                received += len(chunk)
            return file_data
        except Exception as e:
            print(f"接收文件出错: {e}")
            return None
    
    def _send_response(self, client_socket, response):
        """发送响应"""
        try:
            response_data = json.dumps(response).encode()
            response_length = struct.pack('!I', len(response_data))
            client_socket.sendall(response_length + response_data)
        except Exception as e:
            print(f"发送响应出错: {e}")

class P2PClient:
    def __init__(self):
        """初始化P2P客户端"""
        pass
    
    def request_file(self, device_ip, device_port, file_id, group_id):
        """请求文件
        
        Args:
            device_ip: 设备IP
            device_port: 设备端口
            file_id: 文件ID
            group_id: 组ID
            
        Returns:
            bytes: 文件数据
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((device_ip, device_port))
            
            # 发送请求
            request = {'type': 'file_request', 'file_id': file_id, 'group_id': group_id}
            self._send_request(client_socket, request)
            
            # 接收文件
            file_data = self._receive_file(client_socket)
            client_socket.close()
            return file_data
        except Exception as e:
            print(f"请求文件出错: {e}")
            return None
    
    def upload_file(self, device_ip, device_port, file_path, group_id, uploader_id):
        """上传文件
        
        Args:
            device_ip: 设备IP
            device_port: 设备端口
            file_path: 文件路径
            group_id: 组ID
            uploader_id: 上传者ID
            
        Returns:
            dict: 上传结果
        """
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((device_ip, device_port))
            
            # 发送请求
            request = {
                'type': 'file_upload',
                'filename': file_name,
                'size': file_size,
                'group_id': group_id,
                'uploader_id': uploader_id
            }
            self._send_request(client_socket, request)
            
            # 发送文件
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
            
            # 接收响应
            response = self._receive_response(client_socket)
            client_socket.close()
            return response
        except Exception as e:
            print(f"上传文件出错: {e}")
            return {'error': str(e)}
    
    def send_group_invite(self, device_ip, device_port, group_id, group_name, inviter_id):
        """发送组邀请
        
        Args:
            device_ip: 设备IP
            device_port: 设备端口
            group_id: 组ID
            group_name: 组名称
            inviter_id: 邀请者ID
            
        Returns:
            dict: 邀请结果
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((device_ip, device_port))
            
            # 发送请求
            request = {
                'type': 'group_invite',
                'group_id': group_id,
                'group_name': group_name,
                'inviter_id': inviter_id
            }
            self._send_request(client_socket, request)
            
            # 接收响应
            response = self._receive_response(client_socket)
            client_socket.close()
            return response
        except Exception as e:
            print(f"发送组邀请出错: {e}")
            return {'error': str(e)}
    
    def notify_file_change(self, device_ip, device_port, group_id, file_path, change_type):
        """通知文件变化
        
        Args:
            device_ip: 设备IP
            device_port: 设备端口
            group_id: 组ID
            file_path: 文件路径
            change_type: 变化类型
            
        Returns:
            dict: 通知结果
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((device_ip, device_port))
            
            # 发送请求
            request = {
                'type': 'file_change',
                'group_id': group_id,
                'file_path': file_path,
                'change_type': change_type
            }
            self._send_request(client_socket, request)
            
            # 接收响应
            response = self._receive_response(client_socket)
            client_socket.close()
            return response
        except Exception as e:
            print(f"通知文件变化出错: {e}")
            return {'error': str(e)}
    
    def _send_request(self, client_socket, request):
        """发送请求"""
        request_data = json.dumps(request).encode()
        request_length = struct.pack('!I', len(request_data))
        client_socket.sendall(request_length + request_data)
    
    def _receive_file(self, client_socket):
        """接收文件"""
        try:
            # 接收文件大小
            size_data = client_socket.recv(4)
            if not size_data:
                return None
            file_size = struct.unpack('!I', size_data)[0]
            
            # 接收文件数据
            file_data = b''
            received = 0
            while received < file_size:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                file_data += chunk
                received += len(chunk)
            return file_data
        except Exception as e:
            print(f"接收文件出错: {e}")
            return None
    
    def _receive_response(self, client_socket):
        """接收响应"""
        try:
            # 接收响应长度
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            response_length = struct.unpack('!I', length_data)[0]
            
            # 接收响应数据
            response_data = client_socket.recv(response_length)
            return json.loads(response_data.decode())
        except Exception as e:
            print(f"接收响应出错: {e}")
            return None

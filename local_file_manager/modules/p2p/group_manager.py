#!/usr/bin/env python3
"""
P2P组管理模块
"""

import json
import os
import uuid
from datetime import datetime

class GroupManager:
    def __init__(self, config_manager):
        """初始化组管理器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.groups_file = os.path.join(self.config_manager.get_index_dir(), 'p2p_groups.json')
        self.groups = self._load_groups()
        self.members = {}
    
    def _load_groups(self):
        """加载组信息"""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载组信息出错: {e}")
                return {}
        return {}
    
    def _save_groups(self):
        """保存组信息"""
        try:
            os.makedirs(os.path.dirname(self.groups_file), exist_ok=True)
            with open(self.groups_file, 'w', encoding='utf-8') as f:
                json.dump(self.groups, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存组信息出错: {e}")
    
    def create_group(self, group_name, creator_id):
        """创建组
        
        Args:
            group_name: 组名称
            creator_id: 创建者ID
            
        Returns:
            dict: 创建结果
        """
        group_id = str(uuid.uuid4())
        self.groups[group_id] = {
            'id': group_id,
            'name': group_name,
            'creator_id': creator_id,
            'created_at': datetime.now().isoformat(),
            'members': [creator_id],
            'files': []
        }
        self._save_groups()
        return {'success': True, 'group_id': group_id}
    
    def add_member(self, group_id, member_id):
        """添加成员
        
        Args:
            group_id: 组ID
            member_id: 成员ID
            
        Returns:
            dict: 添加结果
        """
        if group_id in self.groups:
            if member_id not in self.groups[group_id]['members']:
                self.groups[group_id]['members'].append(member_id)
                self._save_groups()
                return {'success': True}
            return {'success': False, 'message': '成员已存在'}
        return {'success': False, 'message': '组不存在'}
    
    def remove_member(self, group_id, member_id):
        """移除成员
        
        Args:
            group_id: 组ID
            member_id: 成员ID
            
        Returns:
            dict: 移除结果
        """
        if group_id in self.groups:
            if member_id in self.groups[group_id]['members']:
                self.groups[group_id]['members'].remove(member_id)
                self._save_groups()
                return {'success': True}
            return {'success': False, 'message': '成员不存在'}
        return {'success': False, 'message': '组不存在'}
    
    def delete_group(self, group_id):
        """删除组
        
        Args:
            group_id: 组ID
            
        Returns:
            dict: 删除结果
        """
        if group_id in self.groups:
            del self.groups[group_id]
            self._save_groups()
            return {'success': True}
        return {'success': False, 'message': '组不存在'}
    
    def get_groups(self):
        """获取所有组"""
        return self.groups
    
    def get_group(self, group_id):
        """获取组信息
        
        Args:
            group_id: 组ID
            
        Returns:
            dict: 组信息
        """
        return self.groups.get(group_id)
    
    def add_file_to_group(self, group_id, file_id, filename):
        """添加文件到组
        
        Args:
            group_id: 组ID
            file_id: 文件ID
            filename: 文件名
            
        Returns:
            dict: 添加结果
        """
        if group_id in self.groups:
            file_info = {
                'file_id': file_id,
                'filename': filename,
                'added_at': datetime.now().isoformat()
            }
            self.groups[group_id]['files'].append(file_info)
            self._save_groups()
            return {'success': True}
        return {'success': False, 'message': '组不存在'}
    
    def remove_file_from_group(self, group_id, file_id):
        """从组中移除文件
        
        Args:
            group_id: 组ID
            file_id: 文件ID
            
        Returns:
            dict: 移除结果
        """
        if group_id in self.groups:
            self.groups[group_id]['files'] = [f for f in self.groups[group_id]['files'] if f['file_id'] != file_id]
            self._save_groups()
            return {'success': True}
        return {'success': False, 'message': '组不存在'}
    
    def handle_group_invite(self, group_id, group_name, inviter_id):
        """处理组邀请
        
        Args:
            group_id: 组ID
            group_name: 组名称
            inviter_id: 邀请者ID
            
        Returns:
            dict: 处理结果
        """
        # 这里可以实现邀请处理逻辑
        # 例如，将邀请保存到本地，等待用户确认
        return {'success': True, 'message': '邀请已收到'}
    
    def notify_group_members(self, group_id, notification_type, data):
        """通知组内成员
        
        Args:
            group_id: 组ID
            notification_type: 通知类型
            data: 通知数据
        """
        # 这里可以实现通知逻辑
        # 例如，通过P2P连接发送通知
        pass
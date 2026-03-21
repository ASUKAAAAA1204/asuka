import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore

class TagManager:
    """标签管理系统"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore):
        """初始化标签管理器
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.tag_config_path = os.path.join(config_manager.config_dir, 'tag_config.json')
        self.tags = self._load_tag_config()
    
    def _load_tag_config(self) -> Dict[str, Any]:
        """加载标签配置
        
        Returns:
            标签配置字典
        """
        default_config = {
            'tags': {},
            'tag_groups': {},
            'tag_colors': {}
        }
        
        if os.path.exists(self.tag_config_path):
            try:
                with open(self.tag_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return default_config
    
    def _save_tag_config(self) -> None:
        """保存标签配置"""
        with open(self.tag_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.tags, f, ensure_ascii=False, indent=2)
    
    def add_tag(self, tag_name: str, tag_group: str = '默认', color: str = '#4A90E2') -> Dict[str, Any]:
        """添加标签
        
        Args:
            tag_name: 标签名称
            tag_group: 标签分组
            color: 标签颜色
            
        Returns:
            操作结果
        """
        try:
            # 添加标签到配置
            if tag_name not in self.tags['tags']:
                self.tags['tags'][tag_name] = {
                    'group': tag_group,
                    'color': color
                }
            
            # 添加标签分组
            if tag_group not in self.tags['tag_groups']:
                self.tags['tag_groups'][tag_group] = []
            
            if tag_name not in self.tags['tag_groups'][tag_group]:
                self.tags['tag_groups'][tag_group].append(tag_name)
            
            # 保存配置
            self._save_tag_config()
            
            return {'success': True, 'message': '标签添加成功'}
        except Exception as e:
            return {'success': False, 'message': f'添加标签失败: {str(e)}'}
    
    def remove_tag(self, tag_name: str) -> Dict[str, Any]:
        """删除标签
        
        Args:
            tag_name: 标签名称
            
        Returns:
            操作结果
        """
        try:
            # 从标签配置中删除
            if tag_name in self.tags['tags']:
                tag_group = self.tags['tags'][tag_name]['group']
                del self.tags['tags'][tag_name]
                
                # 从分组中删除
                if tag_group in self.tags['tag_groups']:
                    if tag_name in self.tags['tag_groups'][tag_group]:
                        self.tags['tag_groups'][tag_group].remove(tag_name)
            
            # 保存配置
            self._save_tag_config()
            
            return {'success': True, 'message': '标签删除成功'}
        except Exception as e:
            return {'success': False, 'message': f'删除标签失败: {str(e)}'}
    
    def update_tag(self, tag_name: str, new_name: Optional[str] = None, 
                  tag_group: Optional[str] = None, color: Optional[str] = None) -> Dict[str, Any]:
        """更新标签
        
        Args:
            tag_name: 标签名称
            new_name: 新标签名称
            tag_group: 标签分组
            color: 标签颜色
            
        Returns:
            操作结果
        """
        try:
            if tag_name not in self.tags['tags']:
                return {'success': False, 'message': '标签不存在'}
            
            # 更新标签信息
            if new_name:
                # 从旧分组中删除
                old_group = self.tags['tags'][tag_name]['group']
                if old_group in self.tags['tag_groups']:
                    if tag_name in self.tags['tag_groups'][old_group]:
                        self.tags['tag_groups'][old_group].remove(tag_name)
                
                # 添加到新分组
                self.tags['tags'][new_name] = self.tags['tags'][tag_name]
                del self.tags['tags'][tag_name]
                tag_name = new_name
            
            if tag_group:
                # 从旧分组中删除
                old_group = self.tags['tags'][tag_name]['group']
                if old_group in self.tags['tag_groups']:
                    if tag_name in self.tags['tag_groups'][old_group]:
                        self.tags['tag_groups'][old_group].remove(tag_name)
                
                # 添加到新分组
                self.tags['tags'][tag_name]['group'] = tag_group
                if tag_group not in self.tags['tag_groups']:
                    self.tags['tag_groups'][tag_group] = []
                if tag_name not in self.tags['tag_groups'][tag_group]:
                    self.tags['tag_groups'][tag_group].append(tag_name)
            
            if color:
                self.tags['tags'][tag_name]['color'] = color
            
            # 保存配置
            self._save_tag_config()
            
            return {'success': True, 'message': '标签更新成功'}
        except Exception as e:
            return {'success': False, 'message': f'更新标签失败: {str(e)}'}
    
    def add_tags_to_file(self, file_id: int, tags: List[str]) -> Dict[str, Any]:
        """为文件添加标签
        
        Args:
            file_id: 文件ID
            tags: 标签列表
            
        Returns:
            操作结果
        """
        try:
            # 确保标签存在
            for tag in tags:
                if tag not in self.tags['tags']:
                    self.add_tag(tag)
            
            # 添加标签到文件
            self.data_store.add_tags(file_id, tags)
            
            return {'success': True, 'message': '标签添加成功'}
        except Exception as e:
            return {'success': False, 'message': f'添加标签失败: {str(e)}'}
    
    def remove_tags_from_file(self, file_id: int, tags: List[str]) -> Dict[str, Any]:
        """从文件中移除标签
        
        Args:
            file_id: 文件ID
            tags: 标签列表
            
        Returns:
            操作结果
        """
        try:
            # 获取文件当前标签
            current_tags = self.data_store.get_file_tags(file_id)
            
            # 计算要保留的标签
            remaining_tags = [tag for tag in current_tags if tag not in tags]
            
            # 更新文件标签
            self.data_store.add_tags(file_id, remaining_tags)
            
            return {'success': True, 'message': '标签移除成功'}
        except Exception as e:
            return {'success': False, 'message': f'移除标签失败: {str(e)}'}
    
    def get_file_tags(self, file_id: int) -> List[str]:
        """获取文件的标签
        
        Args:
            file_id: 文件ID
            
        Returns:
            标签列表
        """
        return self.data_store.get_file_tags(file_id)
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签
        
        Returns:
            标签列表
        """
        return list(self.tags['tags'].keys())
    
    def get_tags_by_group(self, group: str) -> List[str]:
        """获取指定分组的标签
        
        Args:
            group: 分组名称
            
        Returns:
            标签列表
        """
        if group in self.tags['tag_groups']:
            return self.tags['tag_groups'][group]
        return []
    
    def get_tag_groups(self) -> List[str]:
        """获取所有标签分组
        
        Returns:
            分组列表
        """
        return list(self.tags['tag_groups'].keys())
    
    def get_tag_info(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """获取标签信息
        
        Args:
            tag_name: 标签名称
            
        Returns:
            标签信息字典
        """
        if tag_name in self.tags['tags']:
            return self.tags['tags'][tag_name]
        return None
    
    def batch_add_tags(self, file_ids: List[int], tags: List[str]) -> Dict[str, Any]:
        """批量为文件添加标签
        
        Args:
            file_ids: 文件ID列表
            tags: 标签列表
            
        Returns:
            操作结果
        """
        try:
            # 确保标签存在
            for tag in tags:
                if tag not in self.tags['tags']:
                    self.add_tag(tag)
            
            # 批量添加标签
            for file_id in file_ids:
                self.data_store.add_tags(file_id, tags)
            
            return {'success': True, 'message': '批量添加标签成功'}
        except Exception as e:
            return {'success': False, 'message': f'批量添加标签失败: {str(e)}'}
    
    def batch_remove_tags(self, file_ids: List[int], tags: List[str]) -> Dict[str, Any]:
        """批量从文件中移除标签
        
        Args:
            file_ids: 文件ID列表
            tags: 标签列表
            
        Returns:
            操作结果
        """
        try:
            # 批量移除标签
            for file_id in file_ids:
                # 获取文件当前标签
                current_tags = self.data_store.get_file_tags(file_id)
                # 计算要保留的标签
                remaining_tags = [tag for tag in current_tags if tag not in tags]
                # 更新文件标签
                self.data_store.add_tags(file_id, remaining_tags)
            
            return {'success': True, 'message': '批量移除标签成功'}
        except Exception as e:
            return {'success': False, 'message': f'批量移除标签失败: {str(e)}'}
    
    def get_files_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """获取包含指定标签的文件
        
        Args:
            tag: 标签名称
            
        Returns:
            文件列表
        """
        # 从数据库中查询包含指定标签的文件
        # 这里需要在DataStore中添加相应的方法
        # 暂时返回空列表
        return []
    
    def get_tag_statistics(self) -> Dict[str, int]:
        """获取标签使用统计
        
        Returns:
            标签使用次数字典
        """
        # 从数据库中统计标签使用次数
        # 这里需要在DataStore中添加相应的方法
        # 暂时返回空字典
        return {}

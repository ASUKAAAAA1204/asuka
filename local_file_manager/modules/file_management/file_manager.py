import os
import shutil
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore

class FileManager:
    """本地文件管理模块"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore):
        """初始化文件管理器
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.storage_dir = config_manager.get_storage_dir()
        self.recycle_bin_dir = os.path.join(self.storage_dir, '回收站')
        self.backup_dir = config_manager.get_backup_dir()
        
        # 确保目录存在
        os.makedirs(self.recycle_bin_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_file_info(self, file_id: int) -> Optional[Dict[str, Any]]:
        """获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息字典
        """
        return self.data_store.get_file(file_id)
    
    def get_files(self, category: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取文件列表
        
        Args:
            category: 分类，None表示所有分类
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            文件信息列表
        """
        return self.data_store.get_files(category, limit, offset)
    
    def delete_file(self, file_id: int) -> Dict[str, Any]:
        """删除文件（移入回收站）
        
        Args:
            file_id: 文件ID
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 构建回收站路径
            filename = file_info['filename']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            recycled_filename = f"{filename}_{timestamp}"
            recycled_path = os.path.join(self.recycle_bin_dir, recycled_filename)
            
            # 移动文件到回收站
            shutil.move(file_info['file_path'], recycled_path)
            
            # 更新数据库中的文件路径
            file_info['file_path'] = recycled_path
            self.data_store.add_file(file_info)
            
            # 从数据库中删除文件
            # self.data_store.delete_file(file_id)
            
            return {'success': True, 'message': '文件已删除并移至回收站'}
        except Exception as e:
            return {'success': False, 'message': f'删除失败: {str(e)}'}
    
    def restore_file(self, file_id: int) -> Dict[str, Any]:
        """从回收站恢复文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 检查文件是否在回收站
            if not file_info['file_path'].startswith(self.recycle_bin_dir):
                return {'success': False, 'message': '文件不在回收站中'}
            
            # 构建原始路径
            original_filename = file_info['filename']
            category = file_info['category']
            original_dir = os.path.join(self.storage_dir, category)
            original_path = os.path.join(original_dir, original_filename)
            
            # 处理文件名冲突
            counter = 1
            base_name, ext = os.path.splitext(original_filename)
            while os.path.exists(original_path):
                new_filename = f"{base_name}_{counter}{ext}"
                original_path = os.path.join(original_dir, new_filename)
                counter += 1
            
            # 移动文件回原始位置
            shutil.move(file_info['file_path'], original_path)
            
            # 更新数据库中的文件路径
            file_info['file_path'] = original_path
            self.data_store.add_file(file_info)
            
            return {'success': True, 'message': '文件已恢复'}
        except Exception as e:
            return {'success': False, 'message': f'恢复失败: {str(e)}'}
    
    def permanently_delete_file(self, file_id: int) -> Dict[str, Any]:
        """永久删除文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 删除文件
            if os.path.exists(file_info['file_path']):
                os.remove(file_info['file_path'])
            
            # 从数据库中删除文件
            self.data_store.delete_file(file_id)
            
            return {'success': True, 'message': '文件已永久删除'}
        except Exception as e:
            return {'success': False, 'message': f'永久删除失败: {str(e)}'}
    
    def move_file(self, file_id: int, new_category: str) -> Dict[str, Any]:
        """移动文件到新分类
        
        Args:
            file_id: 文件ID
            new_category: 新分类
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 构建新路径
            filename = file_info['filename']
            new_dir = os.path.join(self.storage_dir, new_category)
            os.makedirs(new_dir, exist_ok=True)
            new_path = os.path.join(new_dir, filename)
            
            # 处理文件名冲突
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(new_path):
                new_filename = f"{base_name}_{counter}{ext}"
                new_path = os.path.join(new_dir, new_filename)
                counter += 1
            
            # 移动文件
            shutil.move(file_info['file_path'], new_path)
            
            # 更新数据库中的文件路径和分类
            file_info['file_path'] = new_path
            file_info['category'] = new_category
            self.data_store.add_file(file_info)
            
            # 更新分类器中的用户偏好
            from local_file_manager.modules.classification.classifier import Classifier
            classifier = Classifier(self.config_manager)
            classifier.update_user_preference(new_path, new_category)
            
            return {'success': True, 'message': '文件已移动'}
        except Exception as e:
            return {'success': False, 'message': f'移动失败: {str(e)}'}
    
    def copy_file(self, file_id: int, new_category: str) -> Dict[str, Any]:
        """复制文件到新分类
        
        Args:
            file_id: 文件ID
            new_category: 新分类
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 构建新路径
            filename = file_info['filename']
            new_dir = os.path.join(self.storage_dir, new_category)
            os.makedirs(new_dir, exist_ok=True)
            new_path = os.path.join(new_dir, filename)
            
            # 处理文件名冲突
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(new_path):
                new_filename = f"{base_name}_{counter}{ext}"
                new_path = os.path.join(new_dir, new_filename)
                counter += 1
            
            # 复制文件
            shutil.copy2(file_info['file_path'], new_path)
            
            # 创建新的文件信息
            new_file_info = file_info.copy()
            new_file_info['file_path'] = new_path
            new_file_info['category'] = new_category
            
            # 添加到数据库
            new_file_id = self.data_store.add_file(new_file_info)
            
            return {'success': True, 'message': '文件已复制', 'file_id': new_file_id}
        except Exception as e:
            return {'success': False, 'message': f'复制失败: {str(e)}'}
    
    def rename_file(self, file_id: int, new_filename: str) -> Dict[str, Any]:
        """重命名文件
        
        Args:
            file_id: 文件ID
            new_filename: 新文件名
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 构建新路径
            dir_path = os.path.dirname(file_info['file_path'])
            new_path = os.path.join(dir_path, new_filename)
            
            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                return {'success': False, 'message': '文件名已存在'}
            
            # 重命名文件
            os.rename(file_info['file_path'], new_path)
            
            # 更新数据库中的文件路径和文件名
            file_info['file_path'] = new_path
            file_info['filename'] = new_filename
            self.data_store.add_file(file_info)
            
            return {'success': True, 'message': '文件已重命名'}
        except Exception as e:
            return {'success': False, 'message': f'重命名失败: {str(e)}'}
    
    def export_file(self, file_id: int, export_dir: str) -> Dict[str, Any]:
        """导出文件
        
        Args:
            file_id: 文件ID
            export_dir: 导出目录
            
        Returns:
            操作结果
        """
        try:
            # 获取文件信息
            file_info = self.data_store.get_file(file_id)
            if not file_info:
                return {'success': False, 'message': '文件不存在'}
            
            # 确保导出目录存在
            os.makedirs(export_dir, exist_ok=True)
            
            # 构建导出路径
            filename = file_info['filename']
            export_path = os.path.join(export_dir, filename)
            
            # 处理文件名冲突
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(export_path):
                new_filename = f"{base_name}_{counter}{ext}"
                export_path = os.path.join(export_dir, new_filename)
                counter += 1
            
            # 复制文件到导出目录
            shutil.copy2(file_info['file_path'], export_path)
            
            return {'success': True, 'message': '文件已导出', 'export_path': export_path}
        except Exception as e:
            return {'success': False, 'message': f'导出失败: {str(e)}'}
    
    def create_backup(self) -> Dict[str, Any]:
        """创建备份
        
        Returns:
            操作结果
        """
        try:
            # 构建备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 创建备份
            shutil.make_archive(os.path.splitext(backup_path)[0], 'zip', self.storage_dir)
            
            return {'success': True, 'message': '备份已创建', 'backup_path': backup_path}
        except Exception as e:
            return {'success': False, 'message': f'备份失败: {str(e)}'}
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """恢复备份
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            操作结果
        """
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                return {'success': False, 'message': '备份文件不存在'}
            
            # 创建临时目录
            temp_dir = os.path.join(self.backup_dir, 'temp_restore')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 解压备份文件
            shutil.unpack_archive(backup_path, temp_dir)
            
            # 替换存储目录
            backup_storage_dir = os.path.join(temp_dir, os.path.basename(self.storage_dir))
            if os.path.exists(backup_storage_dir):
                # 备份当前存储目录
                current_backup = os.path.join(self.backup_dir, f"current_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.move(self.storage_dir, current_backup)
                
                # 移动备份到存储目录
                shutil.move(backup_storage_dir, self.storage_dir)
                
                # 清理临时目录
                shutil.rmtree(temp_dir)
                
                return {'success': True, 'message': '备份已恢复'}
            else:
                # 清理临时目录
                shutil.rmtree(temp_dir)
                return {'success': False, 'message': '备份文件格式不正确'}
        except Exception as e:
            return {'success': False, 'message': f'恢复失败: {str(e)}'}
    
    def get_recycle_bin_files(self) -> List[Dict[str, Any]]:
        """获取回收站中的文件
        
        Returns:
            文件信息列表
        """
        files = []
        
        # 遍历回收站目录
        for filename in os.listdir(self.recycle_bin_dir):
            file_path = os.path.join(self.recycle_bin_dir, filename)
            if os.path.isfile(file_path):
                # 从数据库中查找文件信息
                file_info = self.data_store.get_file_by_path(file_path)
                if file_info:
                    files.append(file_info)
        
        return files
    
    def empty_recycle_bin(self) -> Dict[str, Any]:
        """清空回收站
        
        Returns:
            操作结果
        """
        try:
            # 获取回收站中的文件
            recycle_bin_files = self.get_recycle_bin_files()
            
            # 删除文件
            for file_info in recycle_bin_files:
                if os.path.exists(file_info['file_path']):
                    os.remove(file_info['file_path'])
                # 从数据库中删除文件
                self.data_store.delete_file(file_info['id'])
            
            return {'success': True, 'message': '回收站已清空'}
        except Exception as e:
            return {'success': False, 'message': f'清空回收站失败: {str(e)}'}
    
    def get_file_content(self, file_id: int) -> Optional[str]:
        """获取文件内容
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件内容字符串，若不存在则返回None
        """
        return self.data_store.get_file_content(file_id)
    
    def save_shared_file(self, filename: str, file_data: bytes, group_id: str, uploader_id: str) -> str:
        """保存共享文件
        
        Args:
            filename: 文件名
            file_data: 文件数据
            group_id: 组ID
            uploader_id: 上传者ID
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 构建共享文件目录
            shared_dir = os.path.join(self.storage_dir, '共享文件', group_id)
            os.makedirs(shared_dir, exist_ok=True)
            
            # 构建文件路径
            file_path = os.path.join(shared_dir, filename)
            
            # 处理文件名冲突
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(shared_dir, new_filename)
                counter += 1
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 导入文件到系统
            from local_file_manager.modules.file_import.file_importer import FileImporter
            file_importer = FileImporter(self.config_manager, self.data_store)
            result = file_importer.import_file(file_path)
            
            return file_path
        except Exception as e:
            print(f"保存共享文件出错: {e}")
            return None
    
    def get_shared_file(self, file_id: str, group_id: str) -> Optional[Dict[str, Any]]:
        """获取共享文件
        
        Args:
            file_id: 文件ID
            group_id: 组ID
            
        Returns:
            dict: 文件信息
        """
        try:
            # 构建共享文件路径
            shared_dir = os.path.join(self.storage_dir, '共享文件', group_id)
            file_path = os.path.join(shared_dir, os.path.basename(file_id))
            
            if os.path.exists(file_path):
                # 获取文件信息
                file_info = self.data_store.get_file_by_path(file_path)
                if not file_info:
                    # 如果文件不在数据库中，创建文件信息
                    file_info = {
                        'filename': os.path.basename(file_path),
                        'file_path': file_path,
                        'size': os.path.getsize(file_path),
                        'file_type': os.path.splitext(file_path)[1][1:].lower() or 'unknown',
                        'category': '共享文件',
                        'created_at': datetime.now().isoformat()
                    }
                return file_info
            return None
        except Exception as e:
            print(f"获取共享文件出错: {e}")
            return None
    
    def handle_file_change(self, group_id: str, file_path: str, change_type: str):
        """处理文件变化
        
        Args:
            group_id: 组ID
            file_path: 文件路径
            change_type: 变化类型
        """
        try:
            # 这里可以实现文件变化的处理逻辑
            # 例如，更新文件信息，通知用户等
            print(f"文件变化: {change_type} - {file_path}")
        except Exception as e:
            print(f"处理文件变化出错: {e}")

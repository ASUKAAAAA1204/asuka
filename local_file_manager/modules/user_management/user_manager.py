import os
import json
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager

class UserManager:
    """用户管理模块"""
    
    def __init__(self, config_manager: ConfigManager):
        """初始化用户管理器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.db_path = os.path.join(config_manager.get_index_dir(), 'user_db.db')
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化用户数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 权限表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT UNIQUE NOT NULL,
                    permissions TEXT NOT NULL
                )
            ''')
            
            # 初始化默认权限
            cursor.execute('SELECT COUNT(*) FROM permissions')
            if cursor.fetchone()[0] == 0:
                default_permissions = {
                    'admin': ['import', 'export', 'delete', 'edit', 'view', 'manage_users', 'manage_settings'],
                    'user': ['import', 'export', 'view', 'edit'],
                    'viewer': ['view']
                }
                
                for role, perms in default_permissions.items():
                    cursor.execute(
                        'INSERT INTO permissions (role, permissions) VALUES (?, ?)',
                        (role, json.dumps(perms))
                    )
            
            # 初始化默认管理员用户（如果不存在）
            cursor.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                admin_password = self._hash_password('admin123')
                cursor.execute(
                    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    ('admin', admin_password, 'admin')
                )
            
            conn.commit()
    
    def _hash_password(self, password: str) -> str:
        """对密码进行哈希处理
        
        Args:
            password: 原始密码
            
        Returns:
            哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """注册新用户
        
        Args:
            username: 用户名
            password: 密码
            role: 用户角色
            
        Returns:
            注册结果
        """
        try:
            # 检查用户名是否已存在
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    return {'success': False, 'message': '用户名已存在'}
                
                # 检查角色是否有效
                cursor.execute('SELECT role FROM permissions WHERE role = ?', (role,))
                if not cursor.fetchone():
                    return {'success': False, 'message': '无效的角色'}
                
                # 创建用户
                password_hash = self._hash_password(password)
                cursor.execute(
                    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    (username, password_hash, role)
                )
                conn.commit()
                
                return {'success': True, 'message': '注册成功'}
        except Exception as e:
            return {'success': False, 'message': f'注册失败: {str(e)}'}
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            登录结果
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, password_hash, role FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
                
                if not user:
                    return {'success': False, 'message': '用户名或密码错误'}
                
                user_id, stored_hash, role = user
                if self._hash_password(password) != stored_hash:
                    return {'success': False, 'message': '用户名或密码错误'}
                
                # 获取用户权限
                cursor.execute('SELECT permissions FROM permissions WHERE role = ?', (role,))
                permissions = cursor.fetchone()
                if permissions:
                    permissions = json.loads(permissions[0])
                else:
                    permissions = []
                
                return {
                    'success': True,
                    'message': '登录成功',
                    'user_id': user_id,
                    'username': username,
                    'role': role,
                    'permissions': permissions
                }
        except Exception as e:
            return {'success': False, 'message': f'登录失败: {str(e)}'}
    
    def get_users(self) -> List[Dict[str, Any]]:
        """获取所有用户
        
        Returns:
            用户列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, role, created_at FROM users')
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row[0],
                        'username': row[1],
                        'role': row[2],
                        'created_at': row[3]
                    })
                return users
        except Exception:
            return []
    
    def update_user_role(self, user_id: int, role: str) -> Dict[str, Any]:
        """更新用户角色
        
        Args:
            user_id: 用户ID
            role: 新角色
            
        Returns:
            更新结果
        """
        try:
            # 检查角色是否有效
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT role FROM permissions WHERE role = ?', (role,))
                if not cursor.fetchone():
                    return {'success': False, 'message': '无效的角色'}
                
                # 更新角色
                cursor.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
                conn.commit()
                
                return {'success': True, 'message': '角色更新成功'}
        except Exception as e:
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除结果
        """
        try:
            # 不允许删除最后一个管理员
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查是否是管理员
                cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
                user_role = cursor.fetchone()
                if user_role and user_role[0] == 'admin':
                    # 检查管理员数量
                    cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
                    if cursor.fetchone()[0] <= 1:
                        return {'success': False, 'message': '不能删除最后一个管理员'}
                
                # 删除用户
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                
                return {'success': True, 'message': '用户删除成功'}
        except Exception as e:
            return {'success': False, 'message': f'删除失败: {str(e)}'}
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            修改结果
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 验证旧密码
                cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
                stored_hash = cursor.fetchone()
                if not stored_hash:
                    return {'success': False, 'message': '用户不存在'}
                
                if self._hash_password(old_password) != stored_hash[0]:
                    return {'success': False, 'message': '旧密码错误'}
                
                # 更新密码
                new_hash = self._hash_password(new_password)
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
                conn.commit()
                
                return {'success': True, 'message': '密码修改成功'}
        except Exception as e:
            return {'success': False, 'message': f'修改失败: {str(e)}'}
    
    def check_permission(self, role: str, permission: str) -> bool:
        """检查用户是否有指定权限
        
        Args:
            role: 用户角色
            permission: 权限名称
            
        Returns:
            是否有该权限
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT permissions FROM permissions WHERE role = ?', (role,))
                permissions = cursor.fetchone()
                if permissions:
                    permissions = json.loads(permissions[0])
                    return permission in permissions
                return False
        except Exception:
            return False

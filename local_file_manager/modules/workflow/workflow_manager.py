import os
import json
import sqlite3
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore
from local_file_manager.modules.file_management.file_manager import FileManager
from local_file_manager.modules.tagging.tag_manager import TagManager

class WorkflowManager:
    """工作流管理模块"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore, file_manager: FileManager, tag_manager: TagManager):
        """初始化工作流管理器
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
            file_manager: 文件管理器
            tag_manager: 标签管理器
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.file_manager = file_manager
        self.tag_manager = tag_manager
        self.workflow_db_path = os.path.join(config_manager.get_index_dir(), 'workflow_db.db')
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化工作流数据库"""
        with sqlite3.connect(self.workflow_db_path) as conn:
            cursor = conn.cursor()
            
            # 工作流表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    config TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 工作流执行日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER,
                    status TEXT NOT NULL,
                    message TEXT,
                    executed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id) ON DELETE CASCADE
                )
            ''')
            
            # 初始化默认工作流
            cursor.execute('SELECT COUNT(*) FROM workflows')
            if cursor.fetchone()[0] == 0:
                # 默认的文件自动分类工作流
                auto_classification_config = {
                    'trigger': 'file_import',
                    'rules': [
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['编程', '技术', '代码', 'API', '开发'],
                            'category': '技术文档'
                        },
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['论文', '研究', '报告', '数据', '分析'],
                            'category': '研究资料'
                        },
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['笔记', '教程', '课程', '学习', '教育'],
                            'category': '学习资料'
                        },
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['方案', '合同', '会议', '工作', '项目'],
                            'category': '工作文档'
                        },
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['日记', '随笔', '灵感', '个人', '生活'],
                            'category': '个人资料'
                        }
                    ]
                }
                
                # 默认的标签推荐工作流
                tag_recommendation_config = {
                    'trigger': 'file_import',
                    'rules': [
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['Python', 'Java', 'C++', 'JavaScript', '编程'],
                            'tags': ['编程', '开发', '技术']
                        },
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['论文', '研究', '学术'],
                            'tags': ['研究', '学术']
                        },
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['会议', '讨论', '总结'],
                            'tags': ['会议', '工作']
                        }
                    ]
                }
                
                # 插入默认工作流
                cursor.execute(
                    'INSERT INTO workflows (name, type, config, enabled) VALUES (?, ?, ?, ?)',
                    ('自动分类', 'auto_classification', json.dumps(auto_classification_config), 1)
                )
                
                cursor.execute(
                    'INSERT INTO workflows (name, type, config, enabled) VALUES (?, ?, ?, ?)',
                    ('标签推荐', 'tag_recommendation', json.dumps(tag_recommendation_config), 1)
                )
            
            conn.commit()
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """获取所有工作流
        
        Returns:
            工作流列表
        """
        try:
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, type, config, enabled, created_at, updated_at FROM workflows')
                workflows = []
                for row in cursor.fetchall():
                    workflows.append({
                        'id': row[0],
                        'name': row[1],
                        'type': row[2],
                        'config': json.loads(row[3]),
                        'enabled': bool(row[4]),
                        'created_at': row[5],
                        'updated_at': row[6]
                    })
                return workflows
        except Exception:
            return []
    
    def add_workflow(self, name: str, workflow_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """添加工作流
        
        Args:
            name: 工作流名称
            workflow_type: 工作流类型
            config: 工作流配置
            
        Returns:
            添加结果
        """
        try:
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO workflows (name, type, config, enabled) VALUES (?, ?, ?, ?)',
                    (name, workflow_type, json.dumps(config), 1)
                )
                conn.commit()
                return {'success': True, 'message': '工作流添加成功'}
        except Exception as e:
            return {'success': False, 'message': f'添加失败: {str(e)}'}
    
    def update_workflow(self, workflow_id: int, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新工作流
        
        Args:
            workflow_id: 工作流ID
            name: 工作流名称
            config: 工作流配置
            
        Returns:
            更新结果
        """
        try:
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE workflows SET name = ?, config = ?, updated_at = ? WHERE id = ?',
                    (name, json.dumps(config), datetime.now().isoformat(), workflow_id)
                )
                conn.commit()
                return {'success': True, 'message': '工作流更新成功'}
        except Exception as e:
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    def delete_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """删除工作流
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            删除结果
        """
        try:
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM workflows WHERE id = ?', (workflow_id,))
                conn.commit()
                return {'success': True, 'message': '工作流删除成功'}
        except Exception as e:
            return {'success': False, 'message': f'删除失败: {str(e)}'}
    
    def toggle_workflow(self, workflow_id: int, enabled: bool) -> Dict[str, Any]:
        """启用/禁用工作流
        
        Args:
            workflow_id: 工作流ID
            enabled: 是否启用
            
        Returns:
            操作结果
        """
        try:
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE workflows SET enabled = ?, updated_at = ? WHERE id = ?',
                    (enabled, datetime.now().isoformat(), workflow_id)
                )
                conn.commit()
                return {'success': True, 'message': '工作流状态更新成功'}
        except Exception as e:
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    def execute_workflow(self, workflow_id: int, file_id: Optional[int] = None) -> Dict[str, Any]:
        """执行工作流
        
        Args:
            workflow_id: 工作流ID
            file_id: 文件ID，可选
            
        Returns:
            执行结果
        """
        try:
            # 获取工作流
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, type, config FROM workflows WHERE id = ? AND enabled = 1', (workflow_id,))
                workflow = cursor.fetchone()
                if not workflow:
                    return {'success': False, 'message': '工作流不存在或已禁用'}
                
                name, workflow_type, config_str = workflow
                config = json.loads(config_str)
                
                # 执行工作流
                if workflow_type == 'auto_classification':
                    result = self._execute_auto_classification(config, file_id)
                elif workflow_type == 'tag_recommendation':
                    result = self._execute_tag_recommendation(config, file_id)
                else:
                    return {'success': False, 'message': '不支持的工作流类型'}
                
                # 记录执行日志
                cursor.execute(
                    'INSERT INTO workflow_logs (workflow_id, status, message) VALUES (?, ?, ?)',
                    (workflow_id, 'success' if result['success'] else 'failed', result['message'])
                )
                conn.commit()
                
                return result
        except Exception as e:
            # 记录错误日志
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO workflow_logs (workflow_id, status, message) VALUES (?, ?, ?)',
                    (workflow_id, 'error', str(e))
                )
                conn.commit()
            return {'success': False, 'message': f'执行失败: {str(e)}'}
    
    def _execute_auto_classification(self, config: Dict[str, Any], file_id: Optional[int] = None) -> Dict[str, Any]:
        """执行自动分类工作流
        
        Args:
            config: 工作流配置
            file_id: 文件ID，可选
            
        Returns:
            执行结果
        """
        try:
            # 确定要处理的文件
            if file_id:
                files = [self.data_store.get_file(file_id)]
            else:
                files = self.data_store.get_files()
            
            processed_count = 0
            for file in files:
                if not file:
                    continue
                
                # 应用分类规则
                content = file.get('content', '')
                filename = file.get('filename', '')
                
                for rule in config.get('rules', []):
                    condition = rule.get('condition')
                    field = rule.get('field')
                    values = rule.get('value', [])
                    category = rule.get('category')
                    
                    if condition == 'contains' and field in ['content', 'filename']:
                        text = content if field == 'content' else filename
                        if any(value in text for value in values):
                            # 更新文件分类
                            self.file_manager.update_file_category(file['id'], category)
                            processed_count += 1
                            break
            
            return {'success': True, 'message': f'自动分类完成，处理了 {processed_count} 个文件'}
        except Exception as e:
            return {'success': False, 'message': f'分类失败: {str(e)}'}
    
    def _execute_tag_recommendation(self, config: Dict[str, Any], file_id: Optional[int] = None) -> Dict[str, Any]:
        """执行标签推荐工作流
        
        Args:
            config: 工作流配置
            file_id: 文件ID，可选
            
        Returns:
            执行结果
        """
        try:
            # 确定要处理的文件
            if file_id:
                files = [self.data_store.get_file(file_id)]
            else:
                files = self.data_store.get_files()
            
            processed_count = 0
            for file in files:
                if not file:
                    continue
                
                # 应用标签规则
                content = file.get('content', '')
                filename = file.get('filename', '')
                
                recommended_tags = []
                for rule in config.get('rules', []):
                    condition = rule.get('condition')
                    field = rule.get('field')
                    values = rule.get('value', [])
                    tags = rule.get('tags', [])
                    
                    if condition == 'contains' and field in ['content', 'filename']:
                        text = content if field == 'content' else filename
                        if any(value in text for value in values):
                            recommended_tags.extend(tags)
                
                # 添加推荐标签
                if recommended_tags:
                    # 去重
                    recommended_tags = list(set(recommended_tags))
                    # 获取现有标签
                    existing_tags = self.tag_manager.get_file_tags(file['id'])
                    # 添加新标签
                    new_tags = [tag for tag in recommended_tags if tag not in existing_tags]
                    if new_tags:
                        self.tag_manager.add_tags_to_file(file['id'], new_tags)
                        processed_count += 1
            
            return {'success': True, 'message': f'标签推荐完成，处理了 {processed_count} 个文件'}
        except Exception as e:
            return {'success': False, 'message': f'标签推荐失败: {str(e)}'}
    
    def get_workflow_logs(self, workflow_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取工作流执行日志
        
        Args:
            workflow_id: 工作流ID，可选
            
        Returns:
            日志列表
        """
        try:
            with sqlite3.connect(self.workflow_db_path) as conn:
                cursor = conn.cursor()
                if workflow_id:
                    cursor.execute('SELECT id, workflow_id, status, message, executed_at FROM workflow_logs WHERE workflow_id = ? ORDER BY executed_at DESC', (workflow_id,))
                else:
                    cursor.execute('SELECT id, workflow_id, status, message, executed_at FROM workflow_logs ORDER BY executed_at DESC')
                
                logs = []
                for row in cursor.fetchall():
                    logs.append({
                        'id': row[0],
                        'workflow_id': row[1],
                        'status': row[2],
                        'message': row[3],
                        'executed_at': row[4]
                    })
                return logs
        except Exception:
            return []

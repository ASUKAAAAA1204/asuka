import os
import json
import platform
from pathlib import Path

class ConfigManager:
    """配置管理模块"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.default_config = self._load_default_config()
        self.config = self._load_config()
    
    def _get_config_dir(self) -> str:
        """获取配置目录"""
        try:
            if platform.system() == 'Windows':
                config_dir = os.path.join(os.environ['APPDATA'], 'LocalFileManager')
            elif platform.system() == 'Darwin':  # macOS
                config_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'LocalFileManager')
            else:  # Linux
                config_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'LocalFileManager')
            
            # 确保配置目录存在，增加错误处理
            try:
                os.makedirs(config_dir, exist_ok=True)
                # 测试目录是否可写
                test_file = os.path.join(config_dir, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                # 如果无法在标准位置创建目录，尝试使用当前目录
                import sys
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                config_dir = os.path.join(base_dir, 'LocalFileManager_Data')
                os.makedirs(config_dir, exist_ok=True)
            
            return config_dir
        except Exception as e:
            # 最后的备用方案：使用当前工作目录
            import tempfile
            config_dir = os.path.join(tempfile.gettempdir(), 'LocalFileManager')
            os.makedirs(config_dir, exist_ok=True)
            return config_dir
    
    def _load_default_config(self) -> dict:
        """加载默认配置"""
        # 先获取配置目录，确保路径可用
        if not hasattr(self, 'config_dir'):
            self.config_dir = self._get_config_dir()
        
        # 尝试在标准位置创建存储目录
        try:
            base_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'LocalFileManager')
            os.makedirs(base_dir, exist_ok=True)
            # 测试目录是否可写
            test_file = os.path.join(base_dir, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception:
            # 如果无法在标准位置创建目录，使用配置目录下的子目录
            base_dir = os.path.join(self.config_dir, 'Storage')
            os.makedirs(base_dir, exist_ok=True)
        
        return {
            'storage': {
                'base_dir': base_dir,
                'index_dir': os.path.join(self.config_dir, 'index'),
                'backup_dir': os.path.join(self.config_dir, 'backup')
            },
            'classification': {
                'enabled': True,
                'categories': {
                    '技术文档': ['编程', '技术', '代码', 'API', '开发'],
                    '研究资料': ['论文', '研究', '报告', '数据', '分析'],
                    '学习资料': ['笔记', '教程', '课程', '学习', '教育'],
                    '工作文档': ['方案', '合同', '会议', '工作', '项目'],
                    '个人资料': ['日记', '随笔', '灵感', '个人', '生活']
                }
            },
            'search': {
                'indexing': True,
                'max_results': 100,
                'min_score': 0.3
            },
            'interface': {
                'theme': 'light',
                'view': 'list',  # list or grid
                'language': 'zh-CN'
            },
            'security': {
                'encryption': False,
                'password_protected': False,
                'backup_frequency': 'daily'  # daily, weekly, monthly
            }
        }
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self.default_config
        else:
            return self.default_config
    
    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key: str, default=None):
        """获取配置值
        
        Args:
            key: 配置键，支持多级键，如 'storage.base_dir'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value) -> None:
        """设置配置值
        
        Args:
            key: 配置键，支持多级键，如 'storage.base_dir'
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def reset_to_default(self) -> None:
        """重置配置到默认值"""
        self.config = self.default_config
        self.save_config()
    
    def get_storage_dir(self) -> str:
        """获取存储目录"""
        base_dir = self.get('storage.base_dir')
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    def get_index_dir(self) -> str:
        """获取索引目录"""
        index_dir = self.get('storage.index_dir')
        os.makedirs(index_dir, exist_ok=True)
        return index_dir
    
    def get_backup_dir(self) -> str:
        """获取备份目录"""
        backup_dir = self.get('storage.backup_dir')
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

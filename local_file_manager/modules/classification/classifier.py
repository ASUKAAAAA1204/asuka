import os
import json
from typing import Dict, List, Any
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager

class Classifier:
    """智能分类系统"""
    
    def __init__(self, config_manager: ConfigManager):
        """初始化分类器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.categories = config_manager.get('classification.categories', {})
        self.feature_library = self._load_feature_library()
        self.user_preferences = self._load_user_preferences()
    
    def _load_feature_library(self) -> Dict[str, List[str]]:
        """加载分类特征库
        
        Returns:
            特征库字典
        """
        # 从配置中加载默认特征库
        feature_library = {}
        for category, keywords in self.categories.items():
            feature_library[category] = keywords
        
        # 可以从文件加载自定义特征库
        feature_lib_path = os.path.join(self.config_manager.config_dir, 'feature_library.json')
        if os.path.exists(feature_lib_path):
            try:
                with open(feature_lib_path, 'r', encoding='utf-8') as f:
                    custom_features = json.load(f)
                    feature_library.update(custom_features)
            except Exception:
                pass
        
        return feature_library
    
    def _load_user_preferences(self) -> Dict[str, str]:
        """加载用户偏好
        
        Returns:
            用户偏好字典，格式为 {file_path: category}
        """
        user_pref_path = os.path.join(self.config_manager.config_dir, 'user_preferences.json')
        if os.path.exists(user_pref_path):
            try:
                with open(user_pref_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_user_preferences(self) -> None:
        """保存用户偏好"""
        user_pref_path = os.path.join(self.config_manager.config_dir, 'user_preferences.json')
        with open(user_pref_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
    
    def classify(self, content: str, keywords: List[Dict[str, Any]], file_path: str = None) -> str:
        """智能分类文件
        
        Args:
            content: 文件内容
            keywords: 关键词列表
            file_path: 文件路径（用于查找用户偏好）
            
        Returns:
            分类结果
        """
        # 首先检查用户偏好
        if file_path and file_path in self.user_preferences:
            return self.user_preferences[file_path]
        
        # 计算每个分类的得分
        scores = self._calculate_scores(content, keywords)
        
        # 返回得分最高的分类
        if scores:
            return max(scores, key=scores.get)
        else:
            return '未分类'
    
    def _calculate_scores(self, content: str, keywords: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算每个分类的得分
        
        Args:
            content: 文件内容
            keywords: 关键词列表
            
        Returns:
            分类得分字典
        """
        scores = {}
        
        # 计算关键词匹配得分
        keyword_scores = self._calculate_keyword_scores(keywords)
        
        # 计算内容匹配得分
        content_scores = self._calculate_content_scores(content)
        
        # 合并得分
        for category in set(keyword_scores.keys()).union(content_scores.keys()):
            scores[category] = keyword_scores.get(category, 0) * 0.7 + content_scores.get(category, 0) * 0.3
        
        return scores
    
    def _calculate_keyword_scores(self, keywords: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算关键词匹配得分
        
        Args:
            keywords: 关键词列表
            
        Returns:
            分类得分字典
        """
        scores = {}
        
        for category, features in self.feature_library.items():
            score = 0
            for kw in keywords:
                if kw['keyword'] in features:
                    score += kw.get('weight', 1.0)
            scores[category] = score
        
        return scores
    
    def _calculate_content_scores(self, content: str) -> Dict[str, float]:
        """计算内容匹配得分
        
        Args:
            content: 文件内容
            
        Returns:
            分类得分字典
        """
        scores = {}
        
        for category, features in self.feature_library.items():
            score = 0
            for feature in features:
                if feature in content:
                    score += 1.0
            scores[category] = score
        
        return scores
    
    def update_user_preference(self, file_path: str, category: str) -> None:
        """更新用户偏好
        
        Args:
            file_path: 文件路径
            category: 用户指定的分类
        """
        self.user_preferences[file_path] = category
        self._save_user_preferences()
        
        # 学习用户偏好，更新特征库
        self._learn_from_preference(file_path, category)
    
    def _learn_from_preference(self, file_path: str, category: str) -> None:
        """从用户偏好中学习
        
        Args:
            file_path: 文件路径
            category: 用户指定的分类
        """
        # 这里可以实现更复杂的学习逻辑
        # 例如，从文件内容中提取特征并添加到特征库
        pass
    
    def get_categories(self) -> List[str]:
        """获取所有分类
        
        Returns:
            分类列表
        """
        return list(self.categories.keys())
    
    def add_category(self, category: str, features: List[str]) -> None:
        """添加新分类
        
        Args:
            category: 分类名称
            features: 分类特征
        """
        self.categories[category] = features
        self.feature_library[category] = features
        
        # 更新配置
        self.config_manager.set('classification.categories', self.categories)
        
        # 保存特征库
        self._save_feature_library()
    
    def remove_category(self, category: str) -> None:
        """移除分类
        
        Args:
            category: 分类名称
        """
        if category in self.categories:
            del self.categories[category]
            
        if category in self.feature_library:
            del self.feature_library[category]
        
        # 更新配置
        self.config_manager.set('classification.categories', self.categories)
        
        # 保存特征库
        self._save_feature_library()
    
    def _save_feature_library(self) -> None:
        """保存特征库"""
        feature_lib_path = os.path.join(self.config_manager.config_dir, 'feature_library.json')
        with open(feature_lib_path, 'w', encoding='utf-8') as f:
            json.dump(self.feature_library, f, ensure_ascii=False, indent=2)

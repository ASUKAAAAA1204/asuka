import os
import shutil
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore
from local_file_manager.modules.file_import.parsers import FileParser
from local_file_manager.modules.classification.classifier import Classifier
from local_file_manager.modules.similarity.similarity_aggregator import SimilarityAggregator
from document_analyzer.api.document_analyzer import DocumentAnalyzer

class FileImporter:
    """文件导入模块"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore):
        """初始化文件导入器
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.parser = FileParser()
        self.classifier = Classifier(config_manager)
        self.similarity_aggregator = SimilarityAggregator(config_manager, data_store)
        self.document_analyzer = DocumentAnalyzer()
        self.storage_dir = config_manager.get_storage_dir()
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保存储目录存在"""
        # 确保主存储目录存在
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # 确保分类子目录存在
        categories = self.config_manager.get('classification.categories', {})
        for category in categories:
            category_dir = os.path.join(self.storage_dir, category)
            os.makedirs(category_dir, exist_ok=True)
        
        # 确保知识簇目录存在
        os.makedirs(os.path.join(self.storage_dir, '知识簇'), exist_ok=True)
        
        # 确保回收站目录存在
        os.makedirs(os.path.join(self.storage_dir, '回收站'), exist_ok=True)
    
    def import_file(self, file_path: str) -> Dict[str, Any]:
        """导入单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            导入结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {'success': False, 'message': f'文件不存在: {file_path}'}
            
            # 获取文件信息
            file_info = self._get_file_info(file_path)
            
            # 解析文件内容
            parse_result = self.parser.parse(file_path)
            if not parse_result['success']:
                return {'success': False, 'message': parse_result['message']}
            
            # 提取文件内容和关键词
            file_content = parse_result.get('content', '')
            keywords = parse_result.get('keywords', [])
            
            # 计算内容哈希
            content_hash = self._calculate_content_hash(file_content)
            file_info['content_hash'] = content_hash
            file_info['content'] = file_content
            
            # 智能分类
            category = self._classify_file(file_content, keywords, file_path)
            file_info['category'] = category
            
            # 复制文件到存储目录
            stored_path = self._store_file(file_path, category)
            file_info['file_path'] = stored_path
            
            # 保存到数据库
            file_id = self.data_store.add_file(file_info)
            
            # 添加关键词
            if keywords:
                self.data_store.add_keywords(file_id, keywords)
            
            # 自动生成标签
            try:
                # 使用文档分析器生成更全面的标签
                tags = self.document_analyzer.generate_tags(stored_path)
                # 添加分类作为标签
                if category not in tags:
                    tags.insert(0, category)
                if tags:
                    self.data_store.add_tags(file_id, tags)
            except Exception as e:
                # 如果文档分析器失败，使用传统方法生成标签
                print(f"文档分析器生成标签失败: {e}")
                tags = self._generate_tags(file_content, keywords, category)
                if tags:
                    self.data_store.add_tags(file_id, tags)
            
            # 更新相似度信息
            self.similarity_aggregator.update_similarity(file_id)
            
            # 检测相似文件
            similar_files = self.similarity_aggregator.find_similar_files(file_id)
            
            # 生成知识簇
            self.similarity_aggregator.generate_clusters()
            
            return {
                'success': True,
                'file_id': file_id,
                'file_path': stored_path,
                'category': category,
                'keywords': keywords,
                'tags': tags,
                'similar_files': similar_files
            }
        except Exception as e:
            return {'success': False, 'message': f'导入失败: {str(e)}'}
    
    def import_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """批量导入文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            导入结果列表
        """
        results = []
        for file_path in file_paths:
            result = self.import_file(file_path)
            results.append(result)
        return results
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        stat = os.stat(file_path)
        return {
            'filename': os.path.basename(file_path),
            'file_type': os.path.splitext(file_path)[1].lower(),
            'size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'metadata': {}
        }
    
    def _calculate_content_hash(self, content: str) -> str:
        """计算内容哈希
        
        Args:
            content: 文件内容
            
        Returns:
            哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _classify_file(self, content: str, keywords: List[Dict[str, Any]], file_path: str = None) -> str:
        """智能分类文件
        
        Args:
            content: 文件内容
            keywords: 关键词列表
            file_path: 文件路径
            
        Returns:
            分类
        """
        return self.classifier.classify(content, keywords, file_path)
    
    def _store_file(self, file_path: str, category: str) -> str:
        """存储文件到对应分类目录
        
        Args:
            file_path: 原文件路径
            category: 分类
            
        Returns:
            存储后的文件路径
        """
        # 构建存储路径
        category_dir = os.path.join(self.storage_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 处理文件名冲突
        filename = os.path.basename(file_path)
        base_name, ext = os.path.splitext(filename)
        stored_path = os.path.join(category_dir, filename)
        
        # 如果文件已存在，添加时间戳
        counter = 1
        while os.path.exists(stored_path):
            new_filename = f"{base_name}_{counter}{ext}"
            stored_path = os.path.join(category_dir, new_filename)
            counter += 1
        
        # 复制文件
        shutil.copy2(file_path, stored_path)
        return stored_path
    
    def _generate_tags(self, content: str, keywords: List[Dict[str, Any]], category: str) -> List[str]:
        """自动生成标签
        
        Args:
            content: 文件内容
            keywords: 关键词列表
            category: 分类
            
        Returns:
            标签列表
        """
        tags = [category]
        
        # 从关键词中选取权重高的作为标签
        sorted_keywords = sorted(keywords, key=lambda x: x.get('weight', 1.0), reverse=True)
        for kw in sorted_keywords[:5]:  # 取前5个关键词
            tags.append(kw['keyword'])
        
        # 去重
        return list(set(tags))
    


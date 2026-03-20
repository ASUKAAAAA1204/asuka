import os
import json
from typing import Dict, List, Any, Set
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore

class SimilarityAggregator:
    """相似内容聚合模块"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore):
        """初始化相似内容聚合器
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.similarity_threshold = config_manager.get('search.min_score', 0.3)
        self.clusters_dir = os.path.join(config_manager.get_storage_dir(), '知识簇')
        os.makedirs(self.clusters_dir, exist_ok=True)
    
    def find_similar_files(self, file_id: int) -> List[Dict[str, Any]]:
        """查找与指定文件相似的文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            相似文件列表，包含相似度分数
        """
        # 从数据库获取相似文件
        similar_files = self.data_store.get_similar_files(file_id, limit=10)
        
        # 过滤掉相似度低于阈值的文件
        return [f for f in similar_files if f['similarity'] >= self.similarity_threshold]
    
    def calculate_similarity(self, file_id1: int, file_id2: int) -> float:
        """计算两个文件之间的相似度
        
        Args:
            file_id1: 文件1 ID
            file_id2: 文件2 ID
            
        Returns:
            相似度分数（0-1）
        """
        # 获取两个文件的关键词
        keywords1 = self.data_store.get_file_keywords(file_id1)
        keywords2 = self.data_store.get_file_keywords(file_id2)
        
        # 计算关键词相似度
        return self._calculate_keyword_similarity(keywords1, keywords2)
    
    def _calculate_keyword_similarity(self, keywords1: List[Dict[str, Any]], keywords2: List[Dict[str, Any]]) -> float:
        """计算关键词相似度
        
        Args:
            keywords1: 文件1的关键词列表
            keywords2: 文件2的关键词列表
            
        Returns:
            相似度分数（0-1）
        """
        if not keywords1 or not keywords2:
            return 0.0
        
        # 提取关键词集合
        kw_set1 = set([kw['keyword'] for kw in keywords1])
        kw_set2 = set([kw['keyword'] for kw in keywords2])
        
        # 计算Jaccard相似度
        intersection = len(kw_set1.intersection(kw_set2))
        union = len(kw_set1.union(kw_set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def build_similarity_network(self) -> None:
        """构建文件相似度网络
        
        计算所有文件之间的相似度，并存储到数据库
        """
        # 获取所有文件
        files = self.data_store.get_files(limit=1000)
        file_ids = [f['id'] for f in files]
        
        # 计算两两文件之间的相似度
        for i in range(len(file_ids)):
            for j in range(i + 1, len(file_ids)):
                file_id1 = file_ids[i]
                file_id2 = file_ids[j]
                
                # 计算相似度
                similarity = self.calculate_similarity(file_id1, file_id2)
                
                # 如果相似度高于阈值，存储到数据库
                if similarity >= self.similarity_threshold:
                    self.data_store.add_similarity(file_id1, file_id2, similarity)
                    self.data_store.add_similarity(file_id2, file_id1, similarity)
    
    def generate_clusters(self) -> List[Dict[str, Any]]:
        """生成知识簇
        
        Returns:
            知识簇列表
        """
        # 获取所有文件
        files = self.data_store.get_files(limit=1000)
        file_ids = set([f['id'] for f in files])
        
        clusters = []
        processed_files = set()
        
        # 使用广度优先搜索生成簇
        for file_id in file_ids:
            if file_id not in processed_files:
                cluster = self._generate_cluster(file_id, processed_files)
                if len(cluster) > 1:  # 只有包含多个文件的簇才保存
                    clusters.append({
                        'cluster_id': len(clusters) + 1,
                        'file_ids': cluster,
                        'size': len(cluster)
                    })
        
        # 保存簇信息
        self._save_clusters(clusters)
        
        return clusters
    
    def _generate_cluster(self, file_id: int, processed_files: Set[int]) -> List[int]:
        """生成单个知识簇
        
        Args:
            file_id: 起始文件ID
            processed_files: 已处理的文件ID集合
            
        Returns:
            簇中的文件ID列表
        """
        cluster = []
        queue = [file_id]
        
        while queue:
            current_file_id = queue.pop(0)
            if current_file_id not in processed_files:
                processed_files.add(current_file_id)
                cluster.append(current_file_id)
                
                # 获取相似文件
                similar_files = self.find_similar_files(current_file_id)
                for similar_file in similar_files:
                    similar_file_id = similar_file['id']
                    if similar_file_id not in processed_files:
                        queue.append(similar_file_id)
        
        return cluster
    
    def _save_clusters(self, clusters: List[Dict[str, Any]]) -> None:
        """保存知识簇信息
        
        Args:
            clusters: 知识簇列表
        """
        clusters_path = os.path.join(self.clusters_dir, 'clusters.json')
        with open(clusters_path, 'w', encoding='utf-8') as f:
            json.dump(clusters, f, ensure_ascii=False, indent=2)
    
    def load_clusters(self) -> List[Dict[str, Any]]:
        """加载知识簇信息
        
        Returns:
            知识簇列表
        """
        clusters_path = os.path.join(self.clusters_dir, 'clusters.json')
        if os.path.exists(clusters_path):
            try:
                with open(clusters_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def get_cluster(self, file_id: int) -> Dict[str, Any]:
        """获取包含指定文件的知识簇
        
        Args:
            file_id: 文件ID
            
        Returns:
            知识簇信息
        """
        clusters = self.load_clusters()
        for cluster in clusters:
            if file_id in cluster['file_ids']:
                return cluster
        return None
    
    def get_cluster_files(self, cluster_id: int) -> List[Dict[str, Any]]:
        """获取知识簇中的文件
        
        Args:
            cluster_id: 知识簇ID
            
        Returns:
            文件列表
        """
        clusters = self.load_clusters()
        for cluster in clusters:
            if cluster['cluster_id'] == cluster_id:
                files = []
                for file_id in cluster['file_ids']:
                    file_info = self.data_store.get_file(file_id)
                    if file_info:
                        files.append(file_info)
                return files
        return []
    
    def update_similarity(self, file_id: int) -> None:
        """更新文件的相似度信息
        
        Args:
            file_id: 文件ID
        """
        # 获取所有其他文件
        files = self.data_store.get_files(limit=1000)
        
        for file in files:
            other_file_id = file['id']
            if other_file_id != file_id:
                # 计算相似度
                similarity = self.calculate_similarity(file_id, other_file_id)
                
                # 如果相似度高于阈值，存储到数据库
                if similarity >= self.similarity_threshold:
                    self.data_store.add_similarity(file_id, other_file_id, similarity)
                    self.data_store.add_similarity(other_file_id, file_id, similarity)
        
        # 重新生成簇
        self.generate_clusters()

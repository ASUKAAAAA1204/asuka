import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore
from local_file_manager.modules.similarity.similarity_aggregator import SimilarityAggregator
from datetime import datetime

class GraphViewer:
    """知识图谱视图模块"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore):
        """初始化知识图谱视图
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.similarity_aggregator = SimilarityAggregator(config_manager, data_store)
        self.graph_cache_path = os.path.join(config_manager.config_dir, 'graph_cache.json')
    
    def generate_graph(self, file_id: Optional[int] = None, include_all: bool = False) -> Dict[str, Any]:
        """生成知识图谱
        
        Args:
            file_id: 文件ID，None表示生成整个图谱
            include_all: 是否包含所有文件
            
        Returns:
            图谱数据，包含节点和边
        """
        nodes = []
        edges = []
        
        if file_id:
            # 生成以指定文件为中心的子图
            nodes, edges = self._generate_subgraph(file_id)
        elif include_all:
            # 生成整个图谱
            nodes, edges = self._generate_full_graph()
        else:
            # 生成最近添加的文件的图谱
            nodes, edges = self._generate_recent_graph()
        
        # 缓存图谱数据
        self._cache_graph(nodes, edges)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _generate_subgraph(self, file_id: int) -> tuple:
        """生成以指定文件为中心的子图
        
        Args:
            file_id: 文件ID
            
        Returns:
            (节点列表, 边列表)
        """
        nodes = []
        edges = []
        
        # 获取中心文件
        center_file = self.data_store.get_file(file_id)
        if not center_file:
            return nodes, edges
        
        # 添加中心节点
        center_node = self._create_node(center_file)
        nodes.append(center_node)
        
        # 获取相似文件
        similar_files = self.similarity_aggregator.find_similar_files(file_id)
        
        # 添加相似文件节点和边
        for similar_file in similar_files:
            similar_node = self._create_node(similar_file)
            nodes.append(similar_node)
            
            # 添加边
            edge = {
                'id': f"{file_id}_{similar_file['id']}",
                'source': file_id,
                'target': similar_file['id'],
                'similarity': similar_file.get('similarity', 0.5)
            }
            edges.append(edge)
        
        return nodes, edges
    
    def _generate_full_graph(self) -> tuple:
        """生成整个图谱
        
        Returns:
            (节点列表, 边列表)
        """
        nodes = []
        edges = []
        
        # 获取所有文件
        files = self.data_store.get_files(limit=1000)
        
        # 添加所有节点
        node_map = {}
        for file in files:
            node = self._create_node(file)
            nodes.append(node)
            node_map[file['id']] = node
        
        # 添加所有边
        # 优化：只计算最近添加的文件与其他文件的相似度
        # 对于已有文件，直接从数据库获取相似度
        recent_files = files[:50]  # 只处理最近50个文件
        existing_files = files[50:]
        
        # 处理最近文件
        for i in range(len(recent_files)):
            file1 = recent_files[i]
            # 与其他最近文件计算相似度
            for j in range(i + 1, len(recent_files)):
                file2 = recent_files[j]
                similarity = self.similarity_aggregator.calculate_similarity(file1['id'], file2['id'])
                if similarity >= self.similarity_aggregator.similarity_threshold:
                    edge = {
                        'id': f"{file1['id']}_{file2['id']}",
                        'source': file1['id'],
                        'target': file2['id'],
                        'similarity': similarity
                    }
                    edges.append(edge)
            
            # 与已有文件计算相似度
            for file2 in existing_files:
                similarity = self.similarity_aggregator.calculate_similarity(file1['id'], file2['id'])
                if similarity >= self.similarity_aggregator.similarity_threshold:
                    edge = {
                        'id': f"{file1['id']}_{file2['id']}",
                        'source': file1['id'],
                        'target': file2['id'],
                        'similarity': similarity
                    }
                    edges.append(edge)
        
        return nodes, edges
    
    def _generate_recent_graph(self) -> tuple:
        """生成最近添加的文件的图谱
        
        Returns:
            (节点列表, 边列表)
        """
        nodes = []
        edges = []
        
        # 获取最近添加的文件
        recent_files = self.data_store.get_files(limit=50)
        
        # 添加最近文件节点
        node_map = {}
        for file in recent_files:
            node = self._create_node(file)
            nodes.append(node)
            node_map[file['id']] = node
        
        # 添加边
        for i in range(len(recent_files)):
            file1 = recent_files[i]
            for j in range(i + 1, len(recent_files)):
                file2 = recent_files[j]
                
                # 计算相似度
                similarity = self.similarity_aggregator.calculate_similarity(file1['id'], file2['id'])
                
                # 如果相似度高于阈值，添加边
                if similarity >= self.similarity_aggregator.similarity_threshold:
                    edge = {
                        'id': f"{file1['id']}_{file2['id']}",
                        'source': file1['id'],
                        'target': file2['id'],
                        'similarity': similarity
                    }
                    edges.append(edge)
        
        return nodes, edges
    
    def _create_node(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """创建节点
        
        Args:
            file_info: 文件信息
            
        Returns:
            节点字典
        """
        # 根据文件类型设置节点颜色
        file_type = file_info.get('file_type', '').lower()
        if file_type == '.pdf':
            color = '#FF5733'
        elif file_type == '.docx':
            color = '#33FF57'
        elif file_type == '.xlsx':
            color = '#3357FF'
        elif file_type == '.txt':
            color = '#F3FF33'
        else:
            color = '#999999'
        
        return {
            'id': file_info['id'],
            'label': file_info['filename'],
            'category': file_info.get('category', '未分类'),
            'file_type': file_type,
            'size': file_info.get('size', 0),
            'color': color,
            'file_path': file_info['file_path']
        }
    
    def _cache_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> None:
        """缓存图谱数据
        
        Args:
            nodes: 节点列表
            edges: 边列表
        """
        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'timestamp': json.dumps(datetime.now(), default=str)
        }
        
        with open(self.graph_cache_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    def load_cached_graph(self) -> Optional[Dict[str, Any]]:
        """加载缓存的图谱数据
        
        Returns:
            图谱数据
        """
        if os.path.exists(self.graph_cache_path):
            try:
                with open(self.graph_cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息
        
        Returns:
            统计信息
        """
        # 获取所有文件
        files = self.data_store.get_files(limit=1000)
        
        # 计算节点数量
        node_count = len(files)
        
        # 计算边数量
        edge_count = 0
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                similarity = self.similarity_aggregator.calculate_similarity(files[i]['id'], files[j]['id'])
                if similarity >= self.similarity_aggregator.similarity_threshold:
                    edge_count += 1
        
        # 计算文件类型分布
        file_type_distribution = {}
        for file in files:
            file_type = file.get('file_type', '').lower()
            if file_type not in file_type_distribution:
                file_type_distribution[file_type] = 0
            file_type_distribution[file_type] += 1
        
        # 计算分类分布
        category_distribution = {}
        for file in files:
            category = file.get('category', '未分类')
            if category not in category_distribution:
                category_distribution[category] = 0
            category_distribution[category] += 1
        
        return {
            'node_count': node_count,
            'edge_count': edge_count,
            'file_type_distribution': file_type_distribution,
            'category_distribution': category_distribution
        }



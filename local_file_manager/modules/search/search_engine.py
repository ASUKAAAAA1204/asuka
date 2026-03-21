import os
import json
import sqlite3
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import OrderedDict

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore

class SearchEngine:
    """智能搜索引擎"""
    
    def __init__(self, config_manager: ConfigManager, data_store: DataStore):
        """初始化搜索引擎
        
        Args:
            config_manager: 配置管理器
            data_store: 数据存储
        """
        self.config_manager = config_manager
        self.data_store = data_store
        self.max_results = config_manager.get('search.max_results', 100)
        self.min_score = config_manager.get('search.min_score', 0.3)
        self._search_cache = OrderedDict()  # 搜索缓存，使用LRU策略
        self._cache_size = 100  # 缓存大小限制
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """执行搜索
        
        Args:
            query: 搜索查询
            **kwargs: 搜索参数
                - search_type: 搜索类型 (keyword, semantic, related)
                - file_types: 文件类型列表
                - categories: 分类列表
                - tags: 标签列表
                - start_date: 开始日期
                - end_date: 结束日期
                - limit: 结果数量限制
                - offset: 结果偏移量
                
        Returns:
            搜索结果列表
        """
        search_type = kwargs.get('search_type', 'keyword')
        limit = kwargs.get('limit', self.max_results)
        
        if search_type == 'keyword':
            results = self._keyword_search(query, **kwargs)
        elif search_type == 'semantic':
            results = self._semantic_search(query, **kwargs)
        elif search_type == 'related':
            results = self._related_search(query, **kwargs)
        elif search_type == 'content':
            results = self._content_search(query, **kwargs)
        else:
            results = self._keyword_search(query, **kwargs)
        
        # 应用过滤器
        results = self._apply_filters(results, **kwargs)
        
        # 限制结果数量
        return results[:limit]
    
    def _keyword_search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """关键词搜索
        
        Args:
            query: 搜索查询
            **kwargs: 搜索参数
                
        Returns:
            搜索结果列表
        """
        # 检查搜索缓存
        cache_key = f"keyword:{query}"
        if cache_key in self._search_cache:
            # 将访问的项移到字典末尾（LRU策略）
            self._search_cache.move_to_end(cache_key)
            return self._search_cache[cache_key]
        
        # 使用数据存储的搜索方法
        results = self.data_store.search_files(query, limit=self.max_results)
        
        # 计算相关性分数
        for result in results:
            result['score'] = self._calculate_relevance_score(result, query)
        
        # 按分数排序
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 缓存搜索结果
        self._search_cache[cache_key] = results
        # 将新项移到字典末尾
        self._search_cache.move_to_end(cache_key)
        # 限制缓存大小
        if len(self._search_cache) > self._cache_size:
            # 删除最旧的缓存项（字典开头）
            self._search_cache.popitem(last=False)
        
        return results
    
    def _semantic_search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """语义搜索
        
        Args:
            query: 搜索查询
            **kwargs: 搜索参数
                
        Returns:
            搜索结果列表
        """
        # 解析自然语言查询
        parsed_query = self._parse_natural_language_query(query)
        
        # 扩展关键词，添加同义词
        extended_keywords = self._expand_keywords(parsed_query['keywords'])
        
        # 构建扩展查询
        if extended_keywords:
            extended_query = ' '.join(extended_keywords)
            results = self._keyword_search(extended_query, **kwargs)
        else:
            results = self._keyword_search(query, **kwargs)
        
        # 应用自然语言查询中的过滤器
        if parsed_query['filters']:
            for key, value in parsed_query['filters'].items():
                kwargs[key] = value
            results = self._apply_filters(results, **kwargs)
        
        # 重新排序结果，基于语义相关性
        results = self._rerank_results(results, query, extended_keywords)
        
        return results
    
    def _parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """解析自然语言查询
        
        Args:
            query: 自然语言查询
            
        Returns:
            解析结果，包含关键词和过滤器
        """
        result = {
            'keywords': [],
            'filters': {}
        }
        
        # 常见的自然语言模式
        patterns = {
            'file_type': [
                (r'\b(?:pdf|文档|文本|图片|视频|音频)\b', lambda m: ('file_types', [m.group(1)])),
            ],
            'category': [
                (r'\b(?:技术|研究|学习|工作|个人)\b(?:文档|资料)?', lambda m: ('categories', [m.group(0)])),
            ],
            'date': [
                (r'\b(?:最近|去年|今年|上月|本月)\b', self._parse_date_expression),
            ],
        }
        
        # 提取关键词
        keywords = re.findall(r'\b\w+\b', query)
        result['keywords'] = keywords
        
        # 应用模式匹配
        for filter_type, pattern_list in patterns.items():
            for pattern, handler in pattern_list:
                match = re.search(pattern, query)
                if match:
                    key, value = handler(match)
                    result['filters'][key] = value
        
        return result
    
    def _parse_date_expression(self, match) -> tuple:
        """解析日期表达式
        
        Args:
            match: 正则表达式匹配结果
            
        Returns:
            (过滤器键, 过滤器值)
        """
        expression = match.group(0)
        # 这里可以添加更复杂的日期解析逻辑
        # 简单实现：返回空过滤器
        return ('start_date', '2024-01-01')
    
    def _expand_keywords(self, keywords: List[str]) -> List[str]:
        """扩展关键词，添加同义词
        
        Args:
            keywords: 原始关键词列表
            
        Returns:
            扩展后的关键词列表
        """
        # 同义词映射
        synonyms = {
            '文档': ['文件', '资料', '文本'],
            '图片': ['图像', '照片', '图片文件'],
            '视频': ['影片', '录像', '视频文件'],
            '音频': ['音乐', '声音', '音频文件'],
            '技术': ['科技', '技术文档', '技术资料'],
            '研究': ['调研', '研究报告', '研究资料'],
            '学习': ['教育', '学习资料', '教材'],
            '工作': ['职场', '工作文档', '办公'],
            '个人': ['私人', '个人资料', '个人文档'],
            'pdf': ['PDF', '文档', '便携式文档格式'],
            'word': ['Word', '文档', '文字处理'],
            'excel': ['Excel', '表格', '电子表格'],
            'ppt': ['PPT', '演示文稿', '幻灯片'],
        }
        
        extended_keywords = []
        for keyword in keywords:
            extended_keywords.append(keyword)
            # 添加同义词
            if keyword in synonyms:
                extended_keywords.extend(synonyms[keyword])
        
        # 去重
        return list(set(extended_keywords))
    
    def _rerank_results(self, results: List[Dict[str, Any]], query: str, extended_keywords: List[str]) -> List[Dict[str, Any]]:
        """重新排序结果，基于语义相关性
        
        Args:
            results: 原始搜索结果
            query: 原始查询
            extended_keywords: 扩展后的关键词
            
        Returns:
            重新排序后的结果
        """
        for result in results:
            # 计算语义相关性分数
            semantic_score = self._calculate_semantic_score(result, query, extended_keywords)
            # 结合原始分数和语义分数
            original_score = result.get('score', 0)
            result['semantic_score'] = 0.7 * original_score + 0.3 * semantic_score
        
        # 按语义分数排序
        results.sort(key=lambda x: x.get('semantic_score', 0), reverse=True)
        return results
    
    def _calculate_semantic_score(self, result: Dict[str, Any], query: str, extended_keywords: List[str]) -> float:
        """计算语义相关性分数
        
        Args:
            result: 文件信息
            query: 原始查询
            extended_keywords: 扩展后的关键词
            
        Returns:
            语义相关性分数（0-1）
        """
        score = 0.0
        
        # 检查文件名与扩展关键词的匹配
        filename_lower = result['filename'].lower()
        for keyword in extended_keywords:
            if keyword.lower() in filename_lower:
                score += 0.1
        
        # 检查分类与扩展关键词的匹配
        category_lower = result['category'].lower()
        for keyword in extended_keywords:
            if keyword.lower() in category_lower:
                score += 0.08
        
        # 检查文件类型与查询的匹配
        file_type_lower = result['file_type'].lower()
        query_lower = query.lower()
        if file_type_lower in query_lower:
            score += 0.15
        
        # 检查文件内容（如果有）
        content = self.data_store.get_file_content(result['id'])
        if content:
            content_lower = content.lower()
            for keyword in extended_keywords:
                if keyword.lower() in content_lower:
                    score += 0.05
        
        # 确保分数在0-1之间
        return min(1.0, score)
    
    def _related_search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """关联搜索
        
        Args:
            query: 搜索查询
            **kwargs: 搜索参数
                
        Returns:
            搜索结果列表
        """
        # 首先执行关键词搜索
        keyword_results = self._keyword_search(query, **kwargs)
        
        if not keyword_results:
            return []
        
        # 获取第一个结果的相似文件
        first_result = keyword_results[0]
        similar_files = self.data_store.get_similar_files(first_result['id'], limit=self.max_results)
        
        # 合并结果
        results = keyword_results + similar_files
        
        # 去重
        seen_ids = set()
        unique_results = []
        for result in results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                unique_results.append(result)
        
        return unique_results
    
    def _content_search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """内容搜索
        
        Args:
            query: 搜索查询
            **kwargs: 搜索参数
                
        Returns:
            搜索结果列表
        """
        # 检查搜索缓存
        cache_key = f"content:{query}"
        if cache_key in self._search_cache:
            # 将访问的项移到字典末尾（LRU策略）
            self._search_cache.move_to_end(cache_key)
            return self._search_cache[cache_key]
        
        # 使用数据存储的内容搜索方法
        results = self.data_store.search_content(query, limit=self.max_results)
        
        # 计算相关性分数
        for result in results:
            result['score'] = self._calculate_content_relevance_score(result, query)
        
        # 按分数排序
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 缓存搜索结果
        self._search_cache[cache_key] = results
        # 将新项移到字典末尾
        self._search_cache.move_to_end(cache_key)
        # 限制缓存大小
        if len(self._search_cache) > self._cache_size:
            # 删除最旧的缓存项（字典开头）
            self._search_cache.popitem(last=False)
        
        return results
    
    def _calculate_content_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """计算文件内容与查询的相关性分数
        
        Args:
            result: 文件信息
            query: 搜索查询
            
        Returns:
            相关性分数（0-1）
        """
        score = 0.0
        
        # 获取文件内容
        content = self.data_store.get_file_content(result['id'])
        if not content:
            return 0.0
        
        # 检查内容匹配
        content_lower = content.lower()
        query_lower = query.lower()
        
        # 完全匹配
        if query_lower in content_lower:
            score += 0.7
        
        # 关键词匹配
        for word in query_lower.split():
            if word in content_lower:
                score += 0.1
        
        # 确保分数在0-1之间
        return min(1.0, score)
    
    def _apply_filters(self, results: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """应用搜索过滤器
        
        Args:
            results: 搜索结果列表
            **kwargs: 搜索参数
                - file_types: 文件类型列表
                - categories: 分类列表
                - tags: 标签列表
                - start_date: 开始日期
                - end_date: 结束日期
                
        Returns:
            过滤后的结果列表
        """
        filtered_results = []
        
        for result in results:
            # 过滤文件类型
            file_types = kwargs.get('file_types', [])
            if file_types and result['file_type'] not in file_types:
                continue
            
            # 过滤分类
            categories = kwargs.get('categories', [])
            if categories and result['category'] not in categories:
                continue
            
            # 过滤标签
            tags = kwargs.get('tags', [])
            if tags:
                file_tags = self.data_store.get_file_tags(result['id'])
                if not any(tag in file_tags for tag in tags):
                    continue
            
            # 过滤日期
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            if start_date and result['created_at'] < start_date:
                continue
            if end_date and result['created_at'] > end_date:
                continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """计算文件与查询的相关性分数
        
        Args:
            result: 文件信息
            query: 搜索查询
            
        Returns:
            相关性分数（0-1）
        """
        score = 0.0
        
        # 检查文件名匹配
        if query.lower() in result['filename'].lower():
            score += 0.5
        
        # 检查分类匹配
        if query.lower() in result['category'].lower():
            score += 0.3
        
        # 检查关键词匹配
        keywords = self.data_store.get_file_keywords(result['id'])
        keyword_list = [kw['keyword'].lower() for kw in keywords]
        for word in query.lower().split():
            if word in keyword_list:
                score += 0.1
        
        # 检查标签匹配
        tags = self.data_store.get_file_tags(result['id'])
        tag_list = [tag.lower() for tag in tags]
        for word in query.lower().split():
            if word in tag_list:
                score += 0.1
        
        # 确保分数在0-1之间
        return min(1.0, score)
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """获取搜索建议
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索建议列表
        """
        suggestions = []
        
        # 从关键词中获取建议
        keywords = self._get_all_keywords()
        for keyword in keywords:
            if keyword.lower().startswith(query.lower()) and keyword not in suggestions:
                suggestions.append(keyword)
        
        # 从标签中获取建议
        tags = self._get_all_tags()
        for tag in tags:
            if tag.lower().startswith(query.lower()) and tag not in suggestions:
                suggestions.append(tag)
        
        # 从分类中获取建议
        categories = self.config_manager.get('classification.categories', {})
        for category in categories:
            if category.lower().startswith(query.lower()) and category not in suggestions:
                suggestions.append(category)
        
        return suggestions[:10]  # 最多返回10个建议
    
    def _get_all_keywords(self) -> List[str]:
        """获取所有关键词
        
        Returns:
            关键词列表
        """
        # 从数据库中获取所有关键词
        db_path = os.path.join(self.config_manager.get_index_dir(), 'file_index.db')
        keywords = []
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT keyword FROM keywords')
                rows = cursor.fetchall()
                keywords = [row[0] for row in rows]
        except Exception:
            pass
        
        return keywords
    
    def _get_all_tags(self) -> List[str]:
        """获取所有标签
        
        Returns:
            标签列表
        """
        # 从数据库中获取所有标签
        db_path = os.path.join(self.config_manager.get_index_dir(), 'file_index.db')
        tags = []
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT tag FROM tags')
                rows = cursor.fetchall()
                tags = [row[0] for row in rows]
        except Exception:
            pass
        
        return tags
    
    def save_search_history(self, query: str) -> None:
        """保存搜索历史
        
        Args:
            query: 搜索查询
        """
        history_path = os.path.join(self.config_manager.config_dir, 'search_history.json')
        
        # 加载历史记录
        history = []
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass
        
        # 添加新查询
        if query not in history:
            history.insert(0, query)
            # 限制历史记录数量
            history = history[:50]
            
            # 保存历史记录
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_search_history(self) -> List[str]:
        """获取搜索历史
        
        Returns:
            搜索历史列表
        """
        history_path = os.path.join(self.config_manager.config_dir, 'search_history.json')
        
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return []
    
    def clear_search_history(self) -> None:
        """清除搜索历史"""
        history_path = os.path.join(self.config_manager.config_dir, 'search_history.json')
        
        if os.path.exists(history_path):
            try:
                os.remove(history_path)
            except Exception:
                pass

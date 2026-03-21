import os
from typing import Dict, List, Tuple, Any
from ..core.extractor import Extractor
from ..core.preprocessor import Preprocessor
from ..core.summarizer import Summarizer
from ..core.keyword import KeywordExtractor

class DocumentAnalyzer:
    """文档分析主类"""
    
    def __init__(self):
        """初始化DocumentAnalyzer"""
        self.extractor = Extractor()
        self.preprocessor = Preprocessor()
        self.summarizer = Summarizer()
        self.keyword_extractor = KeywordExtractor()
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """完整分析文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果，包含元数据、摘要、关键词等
        """
        # 提取文本和元数据
        text, metadata = self.extract_only(file_path)
        
        # 生成摘要
        summary, summary_sentences = self.summarize_only(text, return_details=True)
        
        # 提取关键词
        keywords = self.extract_keywords_only(text)
        
        # 统计信息
        statistics = {
            'total_sentences': len(self.preprocessor.split_sentences(text)),
            'summary_sentences': len(summary_sentences),
            'keyword_count': len(keywords)
        }
        
        # 清理摘要中的空格
        clean_summary = summary.replace(' ', '')
        
        # 构建结果
        result = {
            'metadata': metadata,
            'summary': clean_summary,
            'summary_sentences': summary_sentences,
            'keywords': keywords,
            'statistics': statistics
        }
        
        return result
    
    def extract_only(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """仅提取文本和元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            (文本内容, 元数据字典)
        """
        return self.extractor.extract_with_metadata(file_path)
    
    def summarize_only(self, text: str, max_sentences: int = None, return_details: bool = False) -> Any:
        """仅生成摘要
        
        Args:
            text: 文本
            max_sentences: 最大句子数
            return_details: 是否返回句子详情
            
        Returns:
            如果return_details为True，返回(摘要文本, 句子详情列表)
            否则返回摘要文本
        """
        if return_details:
            return self.summarizer.summarize_with_scores(text, max_sentences)
        else:
            return self.summarizer.summarize(text, max_sentences)
    
    def extract_keywords_only(self, text: str, top_k: int = 10, include_pos: bool = False) -> List[Dict[str, Any]]:
        """仅提取关键词
        
        Args:
            text: 文本
            top_k: 提取的关键词数量
            include_pos: 是否包含词性信息
            
        Returns:
            关键词列表
        """
        if include_pos:
            return self.keyword_extractor.extract_with_pos(text, top_k)
        else:
            return self.keyword_extractor.extract(text, top_k)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析文本内容
        
        Args:
            text: 文本内容
            
        Returns:
            分析结果，包含关键词等
        """
        # 提取关键词
        keywords = self.keyword_extractor.extract(text, top_k=10)
        
        return {
            'keywords': keywords,
            'text': text
        }
    
    def extract_main_info(self, file_path: str) -> Dict[str, Any]:
        """提取文档主要信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含主要信息的字典
        """
        return self.extractor.extract_main_info(file_path)
    
    def generate_tags(self, file_path: str) -> List[str]:
        """根据文档内容生成标签
        
        Args:
            file_path: 文件路径
            
        Returns:
            标签列表
        """
        # 提取主要信息
        main_info = self.extract_main_info(file_path)
        
        # 提取文本内容
        text, _ = self.extract_only(file_path)
        
        # 提取关键词
        keywords = self.extract_keywords_only(text, top_k=15)
        keyword_texts = [kw['keyword'] for kw in keywords]
        
        # 从文件名中提取标签
        filename = main_info['filename']
        filename_tags = self._extract_tags_from_filename(filename)
        
        # 从标题中提取标签
        header_tags = self._extract_tags_from_headers(main_info['headers'])
        
        # 从Excel表头中提取标签
        excel_tags = self._extract_tags_from_excel_headers(main_info['excel_headers'])
        
        # 合并所有标签
        all_tags = keyword_texts + filename_tags + header_tags + excel_tags
        
        # 去重并过滤
        filtered_tags = self._filter_tags(all_tags)
        
        return filtered_tags[:10]  # 最多返回10个标签
    
    def _extract_tags_from_filename(self, filename: str) -> List[str]:
        """从文件名中提取标签
        
        Args:
            filename: 文件名
            
        Returns:
            标签列表
        """
        import re
        import jieba
        
        # 移除文件扩展名
        name = os.path.splitext(filename)[0]
        
        # 分词
        words = jieba.cut(name)
        
        # 过滤短词和数字
        tags = [word.strip() for word in words if len(word.strip()) > 1 and not word.strip().isdigit()]
        
        return tags
    
    def _extract_tags_from_headers(self, headers: List[str]) -> List[str]:
        """从标题中提取标签
        
        Args:
            headers: 标题列表
            
        Returns:
            标签列表
        """
        import re
        import jieba
        
        tags = []
        for header in headers:
            # 移除数字和特殊符号
            cleaned_header = re.sub(r'^[#*\d]+\s*[.、]?\s*', '', header)
            # 分词
            words = jieba.cut(cleaned_header)
            # 过滤短词、数字和特殊符号
            header_tags = [word.strip() for word in words if len(word.strip()) > 1 and not word.strip().isdigit() and not re.match(r'^[#*]+$', word.strip())]
            tags.extend(header_tags)
        
        return tags
    
    def _extract_tags_from_excel_headers(self, excel_headers: List[str]) -> List[str]:
        """从Excel表头中提取标签
        
        Args:
            excel_headers: Excel表头列表
            
        Returns:
            标签列表
        """
        import jieba
        
        tags = []
        for header in excel_headers:
            # 分词
            words = jieba.cut(header)
            # 过滤短词和数字
            header_tags = [word.strip() for word in words if len(word.strip()) > 1 and not word.strip().isdigit()]
            tags.extend(header_tags)
        
        return tags
    
    def _filter_tags(self, tags: List[str]) -> List[str]:
        """过滤标签
        
        Args:
            tags: 标签列表
            
        Returns:
            过滤后的标签列表
        """
        import re
        
        # 去重
        unique_tags = list(set(tags))
        
        # 过滤常见的停用词
        stop_words = {'的', '了', '和', '与', '或', '是', '在', '有', '为', '以', '我们', '你们', '他们', '一个', '可以'}
        
        # 过滤特殊符号和太短的标签
        filtered_tags = []
        for tag in unique_tags:
            # 过滤特殊符号标签
            if re.match(r'^[#*]+$', tag):
                continue
            # 过滤停用词
            if tag in stop_words:
                continue
            # 过滤太短的标签（少于2个字符）
            if len(tag) < 2:
                continue
            filtered_tags.append(tag)
        
        # 按长度排序，优先保留较长的标签
        filtered_tags.sort(key=len, reverse=True)
        
        return filtered_tags
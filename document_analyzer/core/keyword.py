import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from .preprocessor import Preprocessor

class KeywordExtractionError(Exception):
    """关键词提取失败"""
    pass

class KeywordExtractor:
    """关键词提取模块"""
    
    def __init__(self):
        """初始化关键词提取器"""
        self.preprocessor = Preprocessor()
    
    def extract(self, text: str, top_k: int = 10) -> list[dict]:
        """提取关键词
        
        Args:
            text: 文本
            top_k: 提取的关键词数量
            
        Returns:
            关键词列表，每个元素包含关键词和权重
            
        Raises:
            KeywordExtractionError: 关键词提取失败
        """
        try:
            # 清洗文本
            cleaned_text = self.preprocessor.clean_text(text)
            
            # 分词
            words = self.preprocessor.tokenize(cleaned_text)
            
            if not words:
                return []
            
            # 使用TF-IDF提取关键词
            tfidf_keywords = self._extract_tfidf(cleaned_text, top_k)
            
            # 使用TextRank提取关键词
            textrank_keywords = self._extract_textrank(words, top_k)
            
            # 合并结果
            combined_keywords = self._combine_keywords(tfidf_keywords, textrank_keywords, top_k)
            
            return combined_keywords
        except Exception as e:
            raise KeywordExtractionError(f"关键词提取失败: {str(e)}")
    
    def extract_with_pos(self, text: str, top_k: int = 10) -> list[dict]:
        """提取关键词并返回词性
        
        Args:
            text: 文本
            top_k: 提取的关键词数量
            
        Returns:
            关键词列表，每个元素包含关键词、权重和词性
            
        Raises:
            KeywordExtractionError: 关键词提取失败
        """
        try:
            # 清洗文本
            cleaned_text = self.preprocessor.clean_text(text)
            
            # 分词
            words = self.preprocessor.tokenize(cleaned_text)
            
            if not words:
                return []
            
            # 使用TF-IDF提取关键词
            tfidf_keywords = self._extract_tfidf(cleaned_text, top_k)
            
            # 使用TextRank提取关键词
            textrank_keywords = self._extract_textrank(words, top_k)
            
            # 合并结果
            combined_keywords = self._combine_keywords(tfidf_keywords, textrank_keywords, top_k)
            
            # 添加词性信息（简单实现）
            for keyword in combined_keywords:
                keyword['pos'] = self._get_pos(keyword['keyword'])
            
            return combined_keywords
        except Exception as e:
            raise KeywordExtractionError(f"关键词提取失败: {str(e)}")
    
    def _extract_tfidf(self, text: str, top_k: int) -> list[dict]:
        """使用TF-IDF提取关键词
        
        Args:
            text: 文本
            top_k: 提取的关键词数量
            
        Returns:
            关键词列表
        """
        # 使用TF-IDF向量化
        vectorizer = TfidfVectorizer(tokenizer=self.preprocessor.tokenize, lowercase=False, max_features=1000)
        try:
            tfidf_matrix = vectorizer.fit_transform([text])
        except:
            # 如果分词失败，使用简单的词袋模型
            vectorizer = TfidfVectorizer(lowercase=False, max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([text])
        
        # 获取特征词和权重
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # 排序
        indexed_scores = [(score, i) for i, score in enumerate(tfidf_scores)]
        indexed_scores.sort(reverse=True, key=lambda x: x[0])
        
        # 提取前K个关键词
        keywords = []
        for score, i in indexed_scores[:top_k]:
            keywords.append({
                'keyword': feature_names[i],
                'weight': score
            })
        
        return keywords
    
    def _extract_textrank(self, words: list[str], top_k: int) -> list[dict]:
        """使用TextRank提取关键词
        
        Args:
            words: 词语列表
            top_k: 提取的关键词数量
            
        Returns:
            关键词列表
        """
        # 构建词语共现图
        window_size = 2
        co_occurrence = {}
        
        for i, word in enumerate(words):
            for j in range(i + 1, min(i + window_size + 1, len(words))):
                co_word = words[j]
                if word != co_word:
                    if word not in co_occurrence:
                        co_occurrence[word] = {}
                    if co_word not in co_occurrence[word]:
                        co_occurrence[word][co_word] = 0
                    co_occurrence[word][co_word] += 1
        
        # 构建图
        graph = nx.Graph()
        for word, neighbors in co_occurrence.items():
            for neighbor, weight in neighbors.items():
                graph.add_edge(word, neighbor, weight=weight)
        
        # 使用PageRank算法
        if graph.number_of_nodes() > 0:
            scores = nx.pagerank(graph, weight='weight')
        else:
            scores = {}
        
        # 排序
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 提取前K个关键词
        keywords = []
        for word, score in sorted_scores[:top_k]:
            keywords.append({
                'keyword': word,
                'weight': score
            })
        
        return keywords
    
    def _combine_keywords(self, tfidf_keywords: list[dict], textrank_keywords: list[dict], top_k: int) -> list[dict]:
        """合并TF-IDF和TextRank的结果
        
        Args:
            tfidf_keywords: TF-IDF提取的关键词
            textrank_keywords: TextRank提取的关键词
            top_k: 提取的关键词数量
            
        Returns:
            合并后的关键词列表
        """
        # 合并关键词
        keyword_dict = {}
        
        # 为TF-IDF关键词添加权重
        for keyword in tfidf_keywords:
            word = keyword['keyword']
            if word not in keyword_dict:
                keyword_dict[word] = 0
            keyword_dict[word] += keyword['weight'] * 0.5
        
        # 为TextRank关键词添加权重
        for keyword in textrank_keywords:
            word = keyword['keyword']
            if word not in keyword_dict:
                keyword_dict[word] = 0
            keyword_dict[word] += keyword['weight'] * 0.5
        
        # 排序
        sorted_keywords = sorted(keyword_dict.items(), key=lambda x: x[1], reverse=True)
        
        # 提取前K个关键词
        result = []
        for word, weight in sorted_keywords[:top_k]:
            result.append({
                'keyword': word,
                'weight': weight
            })
        
        return result
    
    def _get_pos(self, word: str) -> str:
        """简单的词性判断
        
        Args:
            word: 词语
            
        Returns:
            词性
        """
        # 简单实现，实际项目中可以使用更复杂的词性标注
        if len(word) == 1:
            return '单字'
        elif word.isdigit():
            return '数字'
        elif any(char.isdigit() for char in word):
            return '数字+汉字'
        else:
            return '词语'
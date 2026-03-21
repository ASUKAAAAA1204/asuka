import re
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessor import Preprocessor

class SummaryGenerationError(Exception):
    """摘要生成失败"""
    pass

class Summarizer:
    """摘要生成模块"""
    
    def __init__(self):
        """初始化摘要生成器"""
        self.preprocessor = Preprocessor()
    
    def summarize(self, text: str, max_sentences: int = None) -> str:
        """生成摘要
        
        Args:
            text: 文本
            max_sentences: 最大句子数，None表示自动根据文档长度调整
            
        Returns:
            摘要文本
            
        Raises:
            SummaryGenerationError: 摘要生成失败
        """
        try:
            # 清洗文本
            cleaned_text = self.preprocessor.clean_text(text)
            
            # 分割句子
            sentences = self.preprocessor.split_sentences(cleaned_text)
            # 彻底清理句子中的所有空格，使用与clean_text方法相同的方式
            clean_sentences = []
            for s in sentences:
                # 移除所有空格字符（包括普通空格、制表符、全角空格等）
                s = re.sub(r'\s+', '', s)
                # 移除所有可能的空格字符
                s = re.sub(r'[ \t\n\r\xa0]', '', s)
                clean_sentences.append(s)
            sentences = clean_sentences
            
            if not sentences:
                return ""
            
            # 自动调整摘要长度
            if max_sentences is None:
                text_length = len(cleaned_text)
                if text_length < 1000:
                    max_sentences = 3
                elif text_length < 5000:
                    max_sentences = 5
                else:
                    max_sentences = 8
            
            # 限制最大句子数
            max_sentences = min(max_sentences, len(sentences))
            
            # 计算句子重要性
            sentence_scores, clean_sentences = self._calculate_sentence_scores(sentences)
            
            # 选择得分最高的句子
            top_sentences = self._select_top_sentences(clean_sentences, sentence_scores, max_sentences)
            
            # 按原文顺序排列
            top_sentences.sort(key=lambda x: x[1])
            
            # 构建摘要
            # 确保句子在加入摘要前已经清理了空格
            clean_sentences = []
            for s in top_sentences:
                # 彻底清理句子中的所有空格
                clean_sentence = s[0].strip()
                clean_sentence = clean_sentence.replace(' ', '')
                clean_sentence = re.sub(r'\s+', '', clean_sentence)
                clean_sentences.append(clean_sentence)
            
            summary = '。'.join(clean_sentences) + '。'
            # 最后再次清理整个摘要中的空格
            summary = summary.replace(' ', '')
            summary = re.sub(r'\s+', '', summary)
            # 再次清理，确保所有类型的空格都被移除
            summary = ''.join([c for c in summary if not c.isspace()])
            
            return summary
        except Exception as e:
            raise SummaryGenerationError(f"摘要生成失败: {str(e)}")
    
    def summarize_with_scores(self, text: str, max_sentences: int = None) -> tuple[str, list]:
        """生成摘要并返回句子得分
        
        Args:
            text: 文本
            max_sentences: 最大句子数，None表示自动根据文档长度调整
            
        Returns:
            (摘要文本, 句子详情列表)
            
        Raises:
            SummaryGenerationError: 摘要生成失败
        """
        try:
            # 清洗文本
            cleaned_text = self.preprocessor.clean_text(text)
            
            # 分割句子
            sentences = self.preprocessor.split_sentences(cleaned_text)
            # 彻底清理句子中的所有空格，使用与clean_text方法相同的方式
            clean_sentences = []
            for s in sentences:
                # 移除所有空格字符（包括普通空格、制表符、全角空格等）
                s = re.sub(r'\s+', '', s)
                # 移除所有可能的空格字符
                s = re.sub(r'[ \t\n\r\xa0]', '', s)
                clean_sentences.append(s)
            sentences = clean_sentences
            
            if not sentences:
                return "", []
            
            # 自动调整摘要长度
            if max_sentences is None:
                text_length = len(cleaned_text)
                if text_length < 1000:
                    max_sentences = 3
                elif text_length < 5000:
                    max_sentences = 5
                else:
                    max_sentences = 8
            
            # 限制最大句子数
            max_sentences = min(max_sentences, len(sentences))
            
            # 计算句子重要性
            sentence_scores, clean_sentences = self._calculate_sentence_scores(sentences)
            
            # 选择得分最高的句子
            top_sentences = self._select_top_sentences(clean_sentences, sentence_scores, max_sentences)
            
            # 按原文顺序排列
            top_sentences.sort(key=lambda x: x[1])
            
            # 构建摘要
            # 确保句子在加入摘要前已经清理了空格
            clean_sentences = []
            for s in top_sentences:
                # 彻底清理句子中的所有空格
                clean_sentence = s[0].strip()
                clean_sentence = clean_sentence.replace(' ', '')
                clean_sentence = re.sub(r'\s+', '', clean_sentence)
                clean_sentences.append(clean_sentence)
            
            summary = '。'.join(clean_sentences) + '。'
            # 最后再次清理整个摘要中的空格
            summary = summary.replace(' ', '')
            summary = re.sub(r'\s+', '', summary)
            # 再次清理，确保所有类型的空格都被移除
            summary = ''.join([c for c in summary if not c.isspace()])
            
            # 构建句子详情
            sentence_details = []
            for sentence, index in top_sentences:
                sentence_details.append({
                    'sentence': sentence,
                    'score': sentence_scores[index],
                    'position': index
                })
            
            return summary, sentence_details
        except Exception as e:
            raise SummaryGenerationError(f"摘要生成失败: {str(e)}")
    
    def _calculate_sentence_scores(self, sentences: list[str]) -> tuple[list[float], list[str]]:
        """计算句子重要性得分
        
        Args:
            sentences: 句子列表
            
        Returns:
            (句子得分列表, 清理后的句子列表)
        """
        # 确保所有句子都已经清理了空格
        clean_sentences = [s.replace(' ', '') for s in sentences]
        
        # 使用TF-IDF计算句子向量
        vectorizer = TfidfVectorizer(tokenizer=self.preprocessor.tokenize, lowercase=False)
        try:
            tfidf_matrix = vectorizer.fit_transform(clean_sentences)
        except:
            # 如果分词失败，使用简单的词袋模型
            vectorizer = TfidfVectorizer(lowercase=False)
            tfidf_matrix = vectorizer.fit_transform(clean_sentences)
        
        # 计算句子相似度矩阵
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # 构建相似度图
        graph = nx.from_numpy_array(similarity_matrix)
        
        # 使用PageRank算法计算句子重要性
        scores = nx.pagerank(graph)
        
        # 转换为列表
        sentence_scores = [scores[i] for i in range(len(sentences))]
        
        return sentence_scores, clean_sentences
    
    def _select_top_sentences(self, sentences: list[str], scores: list[float], top_n: int) -> list[tuple[str, int]]:
        """选择得分最高的句子
        
        Args:
            sentences: 句子列表
            scores: 句子得分列表
            top_n: 要选择的句子数
            
        Returns:
            (句子, 索引)列表
        """
        # 排序句子
        indexed_scores = [(score, i) for i, score in enumerate(scores)]
        indexed_scores.sort(reverse=True, key=lambda x: x[0])
        
        # 选择前N个句子
        top_indices = [i for _, i in indexed_scores[:top_n]]
        
        # 返回句子和索引，确保句子已经清理了空格
        return [(sentences[i].replace(' ', ''), i) for i in top_indices]
import re
import jieba
import unicodedata

class Preprocessor:
    """文本预处理模块"""
    
    def __init__(self):
        """初始化预处理器"""
        self.stopwords = self._load_stopwords()
    
    def clean_text(self, text: str) -> str:
        """清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 统一编码为UTF-8
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        # 全半角转换
        text = self._full_to_half(text)
        
        # 去除控制字符
        text = re.sub(r'[\x00-\x1f\x7f]', '', text)
        
        # 移除所有空格字符（包括普通空格、制表符、全角空格等）
        text = re.sub(r'\s+', '', text)
        # 移除所有可能的空格字符
        text = re.sub(r'[ \t\n\r\xa0]', '', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def split_sentences(self, text: str) -> list[str]:
        """分割句子
        
        Args:
            text: 文本
            
        Returns:
            句子列表
        """
        # 使用中文标点符号分割句子
        sentences = re.split(r'[。！？；]', text)
        # 过滤空句子并清理空格
        sentences = [s.strip().replace(' ', '') for s in sentences if s.strip()]
        return sentences
    
    def tokenize(self, text: str) -> list[str]:
        """中文分词
        
        Args:
            text: 文本
            
        Returns:
            词语列表
        """
        # 使用jieba分词
        words = jieba.cut(text)
        # 过滤停用词、空白和无意义字符
        filtered_words = []
        for word in words:
            word = word.strip()
            if word and word not in self.stopwords:
                # 过滤标点符号和特殊字符
                if len(word) > 1 and not all(unicodedata.category(c) in ['P', 'S', 'Z'] for c in word):
                    filtered_words.append(word)
        return filtered_words
    
    def _full_to_half(self, text: str) -> str:
        """全半角转换
        
        Args:
            text: 包含全角字符的文本
            
        Returns:
            转换为半角的文本
        """
        result = []
        for char in text:
            code = ord(char)
            if code == 0x3000:
                # 全角空格转换为半角空格
                result.append(' ')
            elif 0xFF01 <= code <= 0xFF5E:
                # 全角字符转换为半角
                result.append(chr(code - 0xFEE0))
            else:
                result.append(char)
        return ''.join(result)
    
    def _load_stopwords(self) -> set:
        """加载停用词表
        
        Returns:
            停用词集合
        """
        stopwords = set()
        # 内置停用词
        default_stopwords = [
            '的', '了', '和', '是', '在', '我', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
            '我们', '你们', '他们', '什么', '怎么', '这样', '那个', '这个',
            '是', '有', '在', '去', '来', '做', '看', '想', '要', '会', '能',
            '，', '。', '！', '？', '；', '：', '、', '「', '」', '『', '』'
        ]
        for word in default_stopwords:
            stopwords.add(word)
        
        # 尝试加载外部停用词表
        stopwords_path = 'document_analyzer/utils/stopwords.txt'
        try:
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        stopwords.add(word)
        except:
            # 如果文件不存在，使用默认停用词
            pass
        
        return stopwords
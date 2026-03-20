import unittest
import os
import tempfile
from document_analyzer import DocumentAnalyzer
from document_analyzer.core.extractor import Extractor, FileFormatError
from document_analyzer.core.preprocessor import Preprocessor
from document_analyzer.core.summarizer import Summarizer
from document_analyzer.core.keyword import KeywordExtractor

class TestDocumentAnalyzer(unittest.TestCase):
    """测试DocumentAnalyzer类"""
    
    def setUp(self):
        """设置测试环境"""
        self.analyzer = DocumentAnalyzer()
        self.extractor = Extractor()
        self.preprocessor = Preprocessor()
        self.summarizer = Summarizer()
        self.keyword_extractor = KeywordExtractor()
        
        # 创建测试文件
        self.test_txt_content = "这是一个测试文本。这是第二句话。这是第三句话。这是第四句话。这是第五句话。"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_txt_content)
            self.test_txt_file = f.name
    
    def tearDown(self):
        """清理测试文件"""
        if os.path.exists(self.test_txt_file):
            os.remove(self.test_txt_file)
    
    def test_extractor(self):
        """测试文件提取器"""
        # 测试TXT文件提取
        text = self.extractor.extract_text(self.test_txt_file)
        self.assertIn("测试文本", text)
        
        # 测试元数据提取
        text, metadata = self.extractor.extract_with_metadata(self.test_txt_file)
        self.assertIn('filename', metadata)
        self.assertIn('file_size', metadata)
        self.assertIn('word_count', metadata)
        
        # 测试不支持的文件格式
        with tempfile.NamedTemporaryFile(mode='w', suffix='.invalid', delete=False) as f:
            f.write("test")
            invalid_file = f.name
        
        try:
            self.extractor.extract_text(invalid_file)
            self.fail("应该抛出FileFormatError")
        except FileFormatError:
            pass
        finally:
            if os.path.exists(invalid_file):
                os.remove(invalid_file)
    
    def test_preprocessor(self):
        """测试文本预处理器"""
        # 测试文本清洗
        test_text = "  这是  测试  文本！  "
        cleaned = self.preprocessor.clean_text(test_text)
        self.assertEqual(cleaned, "这是测试文本!")
        
        # 测试句子分割
        sentences = self.preprocessor.split_sentences(self.test_txt_content)
        self.assertEqual(len(sentences), 5)
        
        # 测试分词
        words = self.preprocessor.tokenize("这是一个测试文本")
        self.assertGreater(len(words), 0)
    
    def test_summarizer(self):
        """测试摘要生成器"""
        # 测试摘要生成
        summary = self.summarizer.summarize(self.test_txt_content)
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        
        # 测试带得分的摘要生成
        summary, details = self.summarizer.summarize_with_scores(self.test_txt_content)
        self.assertIsInstance(summary, str)
        self.assertIsInstance(details, list)
        self.assertGreater(len(details), 0)
    
    def test_keyword_extractor(self):
        """测试关键词提取器"""
        # 测试关键词提取
        keywords = self.keyword_extractor.extract(self.test_txt_content)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # 测试带词性的关键词提取
        keywords_with_pos = self.keyword_extractor.extract_with_pos(self.test_txt_content)
        self.assertIsInstance(keywords_with_pos, list)
        self.assertGreater(len(keywords_with_pos), 0)
        for keyword in keywords_with_pos:
            self.assertIn('pos', keyword)
    
    def test_document_analyzer(self):
        """测试DocumentAnalyzer主类"""
        # 测试完整分析
        result = self.analyzer.analyze(self.test_txt_file)
        self.assertIn('metadata', result)
        self.assertIn('summary', result)
        self.assertIn('keywords', result)
        self.assertIn('statistics', result)
        
        # 测试仅提取文本
        text, metadata = self.analyzer.extract_only(self.test_txt_file)
        self.assertIsInstance(text, str)
        self.assertIsInstance(metadata, dict)
        
        # 测试仅生成摘要
        summary = self.analyzer.summarize_only(self.test_txt_content)
        self.assertIsInstance(summary, str)
        
        # 测试仅提取关键词
        keywords = self.analyzer.extract_keywords_only(self.test_txt_content)
        self.assertIsInstance(keywords, list)

if __name__ == '__main__':
    unittest.main()

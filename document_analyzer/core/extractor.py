import os
import re
import datetime
import pdfplumber
from docx import Document
from openpyxl import load_workbook

class DocumentAnalyzerError(Exception):
    """基础异常类"""
    pass

class FileFormatError(DocumentAnalyzerError):
    """文件格式不支持"""
    pass

class TextExtractionError(DocumentAnalyzerError):
    """文本提取失败"""
    pass

class Extractor:
    """文件解析模块"""
    
    def extract_text(self, file_path: str) -> str:
        """从文件中提取文本内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
            
        Raises:
            FileFormatError: 文件格式不支持
            TextExtractionError: 文本提取失败
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                return self._extract_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return self._extract_word(file_path)
            elif ext in ['.xlsx', '.xls']:
                return self._extract_excel(file_path)
            elif ext == '.txt':
                return self._extract_txt(file_path)
            else:
                raise FileFormatError(f"不支持的文件格式: {ext}")
        except Exception as e:
            if isinstance(e, DocumentAnalyzerError):
                raise
            raise TextExtractionError(f"文本提取失败: {str(e)}")
    
    def extract_with_metadata(self, file_path: str) -> tuple[str, dict]:
        """从文件中提取文本和元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            (文本内容, 元数据字典)
            
        Raises:
            FileFormatError: 文件格式不支持
            TextExtractionError: 文本提取失败
        """
        text = self.extract_text(file_path)
        metadata = self._extract_metadata(file_path, text)
        return text, metadata
    
    def _extract_pdf(self, file_path: str) -> str:
        """提取PDF文件文本"""
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)
    
    def _extract_word(self, file_path: str) -> str:
        """提取Word文件文本"""
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return '\n'.join(text)
    
    def _extract_excel(self, file_path: str) -> str:
        """提取Excel文件文本"""
        wb = load_workbook(file_path)
        text = []
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            text.append(f"工作表: {sheet_name}")
            for row in sheet.iter_rows(values_only=True):
                row_text = '\t'.join([str(cell) if cell is not None else '' for cell in row])
                if row_text.strip():
                    text.append(row_text)
            text.append('')
        return '\n'.join(text)
    
    def _extract_txt(self, file_path: str) -> str:
        """提取TXT文件文本"""
        encodings = ['utf-8', 'gbk', 'ansi']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                    # 清理所有空格
                    text = text.replace(' ', '')
                    return text
            except UnicodeDecodeError:
                continue
        raise TextExtractionError("无法识别TXT文件编码")
    
    def _extract_metadata(self, file_path: str, text: str) -> dict:
        """提取文件元数据"""
        # 更准确的字数统计，使用分词结果
        import jieba
        words = jieba.cut(text)
        word_count = len([w for w in words if w.strip()])
        
        metadata = {
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'word_count': word_count,
            'char_count': len(text),
            'extracted_at': datetime.datetime.now().isoformat()
        }
        
        # 尝试提取更多元数据
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            try:
                with pdfplumber.open(file_path) as pdf:
                    metadata['pages'] = len(pdf.pages)
            except:
                pass
        elif ext in ['.docx', '.doc']:
            try:
                doc = Document(file_path)
                metadata['paragraphs'] = len(doc.paragraphs)
            except:
                pass
        elif ext in ['.xlsx', '.xls']:
            try:
                wb = load_workbook(file_path)
                metadata['sheets'] = len(wb.sheetnames)
            except:
                pass
        
        return metadata
    
    def extract_main_info(self, file_path: str) -> dict:
        """提取文档主要信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含主要信息的字典，包括文档名称、一级标题、Excel表头等
        """
        ext = os.path.splitext(file_path)[1].lower()
        main_info = {
            'filename': os.path.basename(file_path),
            'headers': [],
            'excel_headers': [],
            'keywords': []
        }
        
        if ext == '.pdf':
            # 提取PDF文件的标题和内容
            text, _ = self.extract_with_metadata(file_path)
            main_info['headers'] = self._extract_headers_from_text(text)
        elif ext in ['.docx', '.doc']:
            # 提取Word文件的标题和内容
            doc = Document(file_path)
            main_info['headers'] = self._extract_word_headers(doc)
        elif ext in ['.xlsx', '.xls']:
            # 提取Excel文件的表头
            main_info['excel_headers'] = self._extract_excel_headers(file_path)
        elif ext == '.txt':
            # 提取TXT文件的标题和内容
            text, _ = self.extract_with_metadata(file_path)
            main_info['headers'] = self._extract_headers_from_text(text)
        
        return main_info
    
    def _extract_headers_from_text(self, text: str) -> list:
        """从文本中提取一级标题
        
        Args:
            text: 文本内容
            
        Returns:
            一级标题列表
        """
        headers = []
        lines = text.split('\n')
        
        # 简单的标题识别规则
        for line in lines:
            line = line.strip()
            if line:
                # 检查是否可能是标题
                # 规则1: 以数字或特殊符号开头，如 "1. 标题" 或 "# 标题"
                if re.match(r'^[#*\d]+\s*[.、]?\s*', line):
                    # 移除开头的特殊符号和数字，只保留标题内容
                    cleaned_line = re.sub(r'^[#*\d]+\s*[.、]?\s*', '', line)
                    if cleaned_line:
                        headers.append(cleaned_line)
                # 规则2: 全大写或包含多个连续的等号/下划线
                elif line.isupper() or re.search(r'[=_{3,}]', line):
                    headers.append(line)
                # 规则3: 长度适中且以冒号结尾
                elif 5 <= len(line) <= 30 and line.endswith('：'):
                    headers.append(line)
        
        return headers[:5]  # 最多返回5个标题
    
    def _extract_word_headers(self, doc) -> list:
        """从Word文档中提取标题
        
        Args:
            doc: Document对象
            
        Returns:
            标题列表
        """
        headers = []
        
        for paragraph in doc.paragraphs:
            # 检查段落样式是否为标题
            if paragraph.style.name.startswith('Heading'):
                headers.append(paragraph.text.strip())
            # 也检查是否有下划线或全大写的段落
            elif paragraph.text.strip() and (paragraph.text.isupper() or '____' in paragraph.text):
                headers.append(paragraph.text.strip())
        
        return headers[:5]  # 最多返回5个标题
    
    def _extract_excel_headers(self, file_path: str) -> list:
        """从Excel文件中提取有用的表头
        
        Args:
            file_path: 文件路径
            
        Returns:
            表头列表
        """
        headers = []
        
        try:
            wb = load_workbook(file_path)
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                # 提取第一行作为表头
                header_row = next(sheet.iter_rows(values_only=True), None)
                if header_row:
                    # 过滤空值和太短的表头
                    sheet_headers = [str(cell) for cell in header_row if cell and len(str(cell)) > 1]
                    if sheet_headers:
                        headers.extend(sheet_headers)
        except Exception as e:
            print(f"提取Excel表头失败: {e}")
        
        # 去重并返回最多10个表头
        return list(set(headers))[:10]
import os
import subprocess
from typing import Dict, Any, List
from pathlib import Path

from document_analyzer.api.document_analyzer import DocumentAnalyzer
from PIL import Image

class FileParser:
    """文件解析器"""
    
    def __init__(self):
        """初始化文件解析器"""
        self.analyzer = DocumentAnalyzer()
        self._parse_cache = {}  # 解析缓存，键为文件路径，值为解析结果
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """解析文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {'success': False, 'message': f'文件不存在: {file_path}'}
            
            # 检查缓存
            file_stat = os.stat(file_path)
            cache_key = f"{file_path}:{file_stat.st_mtime}:{file_stat.st_size}"
            if cache_key in self._parse_cache:
                return self._parse_cache[cache_key]
            
            # 检查文件类型
            file_ext = os.path.splitext(file_path)[1].lower()
            file_type = self._get_file_type(file_ext)
            
            # 根据文件类型选择解析方法
            if file_type == 'text':
                parse_result = self._parse_text_file(file_path)
            elif file_type == 'pdf':
                parse_result = self._parse_pdf_file(file_path)
            elif file_type == 'image':
                parse_result = self._parse_image_file(file_path)
            elif file_type == 'video':
                parse_result = self._parse_video_file(file_path)
            elif file_type == 'audio':
                parse_result = self._parse_audio_file(file_path)
            elif file_type == 'office':
                parse_result = self._parse_office_file(file_path)
            else:
                return {'success': False, 'message': f'不支持的文件类型: {file_ext}'}
            
            # 缓存结果
            if parse_result['success']:
                self._parse_cache[cache_key] = parse_result
                # 限制缓存大小
                if len(self._parse_cache) > 50:
                    # 删除最早的缓存项
                    oldest_key = next(iter(self._parse_cache))
                    del self._parse_cache[oldest_key]
            
            return parse_result
        except Exception as e:
            return {'success': False, 'message': f'解析失败: {str(e)}'}
    
    def _get_file_type(self, file_ext: str) -> str:
        """获取文件类型
        
        Args:
            file_ext: 文件扩展名
            
        Returns:
            文件类型
        """
        text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py']
        pdf_extensions = ['.pdf']
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
        audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.aac']
        office_extensions = ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']
        
        if file_ext in text_extensions:
            return 'text'
        elif file_ext in pdf_extensions:
            return 'pdf'
        elif file_ext in image_extensions:
            return 'image'
        elif file_ext in video_extensions:
            return 'video'
        elif file_ext in audio_extensions:
            return 'audio'
        elif file_ext in office_extensions:
            return 'office'
        else:
            return 'unknown'
    
    def _parse_text_file(self, file_path: str) -> Dict[str, Any]:
        """解析文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 分析内容
            result = self.analyzer.analyze_text(content)
            
            # 提取关键词
            keywords = result.get('keywords', [])
            
            return {
                'success': True,
                'content': content,
                'keywords': keywords,
                'file_type': 'text'
            }
        except Exception as e:
            return {'success': False, 'message': f'解析文本文件失败: {str(e)}'}
    
    def _parse_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """解析PDF文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            # 使用DocumentAnalyzer分析PDF文件
            result = self.analyzer.analyze(file_path)
            
            # 提取内容和关键词
            content = ' '.join([sent['sentence'] for sent in result.get('summary_sentences', [])])
            keywords = result.get('keywords', [])
            
            return {
                'success': True,
                'content': content,
                'keywords': keywords,
                'file_type': 'pdf'
            }
        except Exception as e:
            return {'success': False, 'message': f'解析PDF文件失败: {str(e)}'}
    
    def _parse_image_file(self, file_path: str) -> Dict[str, Any]:
        """解析图片文件（OCR）
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            # 尝试使用OCR提取文本
            # 这里使用pytesseract作为示例，实际应用中可能需要安装相应依赖
            try:
                # 动态导入pytesseract
                import pytesseract

                # 打开图片
                img = Image.open(file_path)
                # 进行OCR
                content = pytesseract.image_to_string(img, lang='chi_sim+eng')
                
                # 分析提取的文本
                if content.strip():
                    result = self.analyzer.analyze_text(content)
                    keywords = result.get('keywords', [])
                else:
                    content = '图片文件（无文本内容）'
                    keywords = []
                
                return {
                    'success': True,
                    'content': content,
                    'keywords': keywords,
                    'file_type': 'image',
                    'ocr_applied': True
                }
            except ImportError:
                # OCR依赖未安装，返回基本信息
                return {
                    'success': True,
                    'content': '图片文件（OCR功能未启用）',
                    'keywords': [],
                    'file_type': 'image',
                    'ocr_applied': False
                }
        except Exception as e:
            return {'success': False, 'message': f'解析图片文件失败: {str(e)}'}
    
    def _parse_video_file(self, file_path: str) -> Dict[str, Any]:
        """解析视频文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            # 获取视频文件信息
            file_size = os.path.getsize(file_path)
            
            # 尝试使用ffmpeg获取视频信息（如果可用）
            try:
                import ffmpeg
                probe = ffmpeg.probe(file_path)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if video_stream:
                    duration = float(video_stream.get('duration', 0))
                    resolution = f"{video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}"
                else:
                    duration = 0
                    resolution = 'N/A'
            except ImportError:
                duration = 0
                resolution = 'N/A'
            
            # 构建内容描述
            content = f"视频文件\n大小: {self._format_size(file_size)}\n时长: {self._format_duration(duration)}\n分辨率: {resolution}"
            
            return {
                'success': True,
                'content': content,
                'keywords': ['视频', '媒体'],
                'file_type': 'video'
            }
        except Exception as e:
            return {'success': False, 'message': f'解析视频文件失败: {str(e)}'}
    
    def _parse_audio_file(self, file_path: str) -> Dict[str, Any]:
        """解析音频文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            # 获取音频文件信息
            file_size = os.path.getsize(file_path)
            
            # 尝试使用ffmpeg获取音频信息（如果可用）
            try:
                import ffmpeg
                probe = ffmpeg.probe(file_path)
                audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
                if audio_stream:
                    duration = float(audio_stream.get('duration', 0))
                    sample_rate = audio_stream.get('sample_rate', 'N/A')
                else:
                    duration = 0
                    sample_rate = 'N/A'
            except ImportError:
                duration = 0
                sample_rate = 'N/A'
            
            # 构建内容描述
            content = f"音频文件\n大小: {self._format_size(file_size)}\n时长: {self._format_duration(duration)}\n采样率: {sample_rate}Hz"
            
            return {
                'success': True,
                'content': content,
                'keywords': ['音频', '媒体'],
                'file_type': 'audio'
            }
        except Exception as e:
            return {'success': False, 'message': f'解析音频文件失败: {str(e)}'}
    
    def _parse_office_file(self, file_path: str) -> Dict[str, Any]:
        """解析Office文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果
        """
        try:
            # 使用DocumentAnalyzer分析Office文件
            result = self.analyzer.analyze(file_path)
            
            # 提取完整内容和关键词
            # 直接使用提取的完整文本，而不是仅使用摘要
            text, _ = self.analyzer.extract_only(file_path)
            content = text
            keywords = result.get('keywords', [])
            
            return {
                'success': True,
                'content': content,
                'keywords': keywords,
                'file_type': 'office'
            }
        except Exception as e:
            return {'success': False, 'message': f'解析Office文件失败: {str(e)}'}
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小
        
        Args:
            size: 文件大小（字节）
            
        Returns:
            格式化后的大小字符串
        """
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def _format_duration(self, seconds: float) -> str:
        """格式化时长
        
        Args:
            seconds: 时长（秒）
            
        Returns:
            格式化后的时长字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}时{minutes}分{secs}秒"

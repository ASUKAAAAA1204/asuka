#!/usr/bin/env python3
"""
文件项控件模块
"""

import os
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QAction, QDialog, QTextEdit, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

class FileItemWidget(QWidget):
    """文件项控件"""
    def __init__(self, file_info, file_manager=None):
        super().__init__()
        self.file_info = file_info
        self.file_manager = file_manager
        
        # 透明度效果
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1)
        
        # 设置卡片样式
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
            QWidget:hover {
                border: 1px solid #E3F2FD;
            }
        """)
        
        # 启用上下文菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 文件图标和名称
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # 文件图标
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon = self._get_file_icon(self.file_info.get('file_type', 'unknown'))
        icon_label.setPixmap(icon.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
        header_layout.addWidget(icon_label)
        
        # 文件信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        filename_label = QLabel(self.file_info['filename'])
        filename_label.setFont(QFont('微软雅黑', 10, QFont.Weight.Medium))
        filename_label.setStyleSheet("color: #212121;")
        filename_label.setWordWrap(True)
        info_layout.addWidget(filename_label)
        
        details = f"{self.file_info.get('file_type', 'unknown')} | {self.file_info.get('category', '未分类')} | {self._format_size(self.file_info.get('size', 0))}"
        details_label = QLabel(details)
        details_label.setFont(QFont('Times New Roman', 8))
        details_label.setStyleSheet("color: #757575;")
        info_layout.addWidget(details_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 标签（如果有）
        tags = self.file_info.get('tags', [])
        if tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(8)
            
            for tag in tags[:3]:  # 最多显示3个标签
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""QLabel {
                    background-color: #E3F2FD;
                    color: #1976D2;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 8px;
                    font-family: '微软雅黑', 'Times New Roman';
                }""")
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        
        self.setLayout(layout)
    
    def setOpacity(self, opacity):
        """设置透明度"""
        self.opacity_effect.setOpacity(opacity)
    
    def show_context_menu(self, pos):
        """显示上下文菜单"""
        menu = QMenu()
        
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_file)
        menu.addAction(open_action)
        
        if self.file_manager:
            view_content_action = QAction("查看内容", self)
            view_content_action.triggered.connect(self.view_file_content)
            menu.addAction(view_content_action)
            
            rename_action = QAction("重命名", self)
            rename_action.triggered.connect(self.rename_file)
            menu.addAction(rename_action)
            
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(self.delete_file)
            menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def open_file(self):
        """打开文件"""
        if 'file_path' in self.file_info:
            file_path = self.file_info['file_path']
            if os.path.exists(file_path):
                os.startfile(file_path) if sys.platform == 'win32' else os.system(f'open "{file_path}"')
    
    def view_file_content(self):
        """查看文件内容"""
        if not self.file_manager or 'id' not in self.file_info:
            return
        
        file_id = self.file_info['id']
        filename = self.file_info['filename']
        
        # 获取文件内容
        content = self.file_manager.get_file_content(file_id)
        
        if not content:
            QMessageBox.information(self, "提示", "文件内容不存在或无法读取")
            return
        
        # 创建内容查看对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"查看文件内容 - {filename}")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # 文本编辑框，用于显示内容
        text_edit = QTextEdit()
        text_edit.setPlainText(content)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont('Times New Roman', 6))
        layout.addWidget(text_edit)
        
        # 关闭按钮
        from PyQt6.QtWidgets import QHBoxLayout, QPushButton
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def rename_file(self):
        """重命名文件"""
        if not self.file_manager or 'id' not in self.file_info:
            return
        
        file_id = self.file_info['id']
        old_name = self.file_info['filename']
        
        new_name, ok = QInputDialog.getText(self, "重命名文件", "请输入新文件名:", text=old_name)
        if ok and new_name:
            result = self.file_manager.rename_file(file_id, new_name)
            if result['success']:
                QMessageBox.information(self, "成功", "文件重命名成功")
                # 刷新父控件的文件列表
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'refresh_files'):
                        parent.refresh_files()
                        break
                    parent = parent.parent()
            else:
                QMessageBox.warning(self, "失败", f"文件重命名失败: {result['message']}")
    
    def delete_file(self):
        """删除文件"""
        if not self.file_manager or 'id' not in self.file_info:
            return
        
        file_id = self.file_info['id']
        filename = self.file_info['filename']
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除文件 {filename} 吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.file_manager.delete_file(file_id)
            if result['success']:
                QMessageBox.information(self, "成功", "文件删除成功")
                # 刷新父控件的文件列表
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'refresh_files'):
                        parent.refresh_files()
                        break
                    parent = parent.parent()
            else:
                QMessageBox.warning(self, "失败", f"文件删除失败: {result['message']}")
    
    def _get_file_icon(self, file_type):
        """获取文件图标"""
        # 创建圆形倒角的正方形图标，使用上下渐变过渡
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor('#FFFFFF'))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 标准化文件类型（移除点号并转换为小写）
        if file_type.startswith('.'):
            file_type = file_type[1:].lower()
        else:
            file_type = file_type.lower()
        
        # 定义颜色对
        color_pairs = {
            'txt': ('#666666', '#CCCCCC'),       # 深灰和浅灰
            'pdf': ('#DDA0DD', '#FFB6C1'),       # 浅紫和浅粉色
            'jpg': ('#2ECC71', '#81C784'),       # 深绿和浅绿（图片）
            'jpeg': ('#2ECC71', '#81C784'),      # 深绿和浅绿（图片）
            'png': ('#2ECC71', '#81C784'),       # 深绿和浅绿（图片）
            'gif': ('#2ECC71', '#81C784'),       # 深绿和浅绿（图片）
            'bmp': ('#2ECC71', '#81C784'),       # 深绿和浅绿（图片）
            'tiff': ('#2ECC71', '#81C784'),      # 深绿和浅绿（图片）
            'mp4': ('#F39C12', '#FFB74D'),       # 深橙和浅橙（视频）
            'avi': ('#F39C12', '#FFB74D'),       # 深橙和浅橙（视频）
            'mov': ('#F39C12', '#FFB74D'),       # 深橙和浅橙（视频）
            'wmv': ('#F39C12', '#FFB74D'),       # 深橙和浅橙（视频）
            'flv': ('#F39C12', '#FFB74D'),       # 深橙和浅橙（视频）
            'mkv': ('#F39C12', '#FFB74D'),       # 深橙和浅橙（视频）
            'mp3': ('#9B59B6', '#BA68C8'),       # 深紫和浅紫（音频）
            'wav': ('#9B59B6', '#BA68C8'),       # 深紫和浅紫（音频）
            'ogg': ('#9B59B6', '#BA68C8'),       # 深紫和浅紫（音频）
            'flac': ('#9B59B6', '#BA68C8'),      # 深紫和浅紫（音频）
            'aac': ('#9B59B6', '#BA68C8'),       # 深紫和浅紫（音频）
            'xlsx': ('#2E7D32', '#81C784'),      # 深绿与浅绿
            'xls': ('#2E7D32', '#81C784'),       # 深绿与浅绿
            'docx': ('#1565C0', '#64B5F6'),      # 深蓝和浅蓝
            'doc': ('#1565C0', '#64B5F6'),       # 深蓝和浅蓝
            'pptx': ('#C62828', '#EF9A9A'),      # 深红和浅红
            'ppt': ('#C62828', '#EF9A9A'),       # 深红和浅红
        }
        
        # 获取颜色对，如果没有找到则使用默认颜色
        if file_type in color_pairs:
            color1, color2 = color_pairs[file_type]
        else:
            color1, color2 = '#95A5A6', '#BDBDBD'  # 默认深灰和浅灰
        
        # 绘制圆形倒角的正方形（圆角矩形）
        rect = pixmap.rect()
        radius = 8  # 圆角半径
        
        # 创建渐变
        from PyQt6.QtGui import QLinearGradient
        gradient = QLinearGradient(0, 0, 0, 48)  # 上下渐变
        gradient.setColorAt(0, QColor(color1))  # 顶部颜色
        gradient.setColorAt(1, QColor(color2))  # 底部颜色
        
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)
        
        # 在图标右上角添加字母标记
        painter.setPen(QColor('#FFFFFF'))  # 白色文字
        painter.setFont(QFont('Times New Roman', 12, QFont.Weight.Bold))  # TIMES NEW ROMAN加粗字体
        
        # 根据文件类型添加不同的字母
        if file_type in ['xlsx', 'xls']:
            # Excel：添加'X'
            painter.drawText(32, 8, 16, 16, Qt.AlignmentFlag.AlignCenter, 'X')
        elif file_type in ['docx', 'doc']:
            # Word：添加'W'
            painter.drawText(32, 8, 16, 16, Qt.AlignmentFlag.AlignCenter, 'W')
        elif file_type in ['pptx', 'ppt', 'pdf']:
            # PPT和PDF：添加'P'
            painter.drawText(32, 8, 16, 16, Qt.AlignmentFlag.AlignCenter, 'P')
        elif file_type == 'txt':
            # TXT：添加'T'
            painter.drawText(32, 8, 16, 16, Qt.AlignmentFlag.AlignCenter, 'T')
        
        painter.end()
        return pixmap
    
    def _format_size(self, size):
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"

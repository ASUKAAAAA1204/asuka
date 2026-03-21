#!/usr/bin/env python3
"""
UI工具模块
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QColor

class ToastNotification(QWidget):
    """Toast通知类"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""QLabel {
            color: white;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            padding: 12px 24px;
            border-radius: 8px;
        }""")
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # 动画
        self.animation = None
        
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
    def show_notification(self, message, type="info", duration=3000):
        """显示通知"""
        # 设置背景颜色
        if type == "success":
            self.label.setStyleSheet("""QLabel {
                color: white;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                padding: 12px 24px;
                border-radius: 8px;
                background-color: #4CAF50;
            }""")
        elif type == "error":
            self.label.setStyleSheet("""QLabel {
                color: white;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                padding: 12px 24px;
                border-radius: 8px;
                background-color: #F44336;
            }""")
        elif type == "warning":
            self.label.setStyleSheet("""QLabel {
                color: #212121;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                padding: 12px 24px;
                border-radius: 8px;
                background-color: #FFC107;
            }""")
        else:
            self.label.setStyleSheet("""QLabel {
                color: white;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                padding: 12px 24px;
                border-radius: 8px;
                background-color: #2196F3;
            }""")
        
        self.label.setText(message)
        self.adjustSize()
        
        # 定位到右上角
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.top() + 60  # 避开顶部导航栏
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
            x = screen_rect.width() - self.width() - 20
            y = 60
        
        self.setGeometry(x, y, self.width(), self.height())
        self.show()
        
        # 动画效果
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
        
        # 滑入动画
        slide_anim = QPropertyAnimation(self, b"pos")
        slide_anim.setDuration(300)
        slide_anim.setStartValue(QPoint(x + 200, y))
        slide_anim.setEndValue(QPoint(x, y))
        slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 淡入动画
        fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_anim.setDuration(300)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        
        # 启动动画
        slide_anim.start()
        fade_anim.start()
        
        # 错误通知添加抖动效果
        if type == "error":
            shake_anim = QPropertyAnimation(self, b"pos")
            shake_anim.setDuration(500)
            shake_anim.setKeyValueAt(0, QPoint(x, y))
            shake_anim.setKeyValueAt(0.2, QPoint(x - 10, y))
            shake_anim.setKeyValueAt(0.4, QPoint(x + 10, y))
            shake_anim.setKeyValueAt(0.6, QPoint(x - 10, y))
            shake_anim.setKeyValueAt(0.8, QPoint(x + 10, y))
            shake_anim.setKeyValueAt(1, QPoint(x, y))
            shake_anim.start()
        
        # 自动隐藏
        QTimer.singleShot(duration, self.hide_notification)
    
    def hide_notification(self):
        """隐藏通知"""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        # 滑出动画
        slide_anim = QPropertyAnimation(self, b"pos")
        slide_anim.setDuration(200)
        slide_anim.setStartValue(self.pos())
        slide_anim.setEndValue(QPoint(self.x() + 200, self.y()))
        slide_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # 淡出动画
        fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_anim.setDuration(200)
        fade_anim.setStartValue(1)
        fade_anim.setEndValue(0)
        
        # 连接动画结束信号
        slide_anim.finished.connect(self.hide)
        
        # 启动动画
        slide_anim.start()
        fade_anim.start()

class LoadingWidget(QWidget):
    """加载状态动画"""
    def __init__(self, parent=None, text="加载中..."):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 加载动画
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # 加载文本
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("color: #2196F3; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        layout.addWidget(self.text_label)
        
        self.setLayout(layout)
        
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
        # 启动动画
        self._start_animation()
    
    def _start_animation(self):
        """启动加载动画"""
        from PyQt6.QtCore import QTimer
        
        self.loading_text = ["●", "●●", "●●●"]
        self.current_frame = 0
        
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(200)
    
    def _update_animation(self):
        """更新动画帧"""
        self.loading_label.setText(self.loading_text[self.current_frame])
        self.loading_label.setStyleSheet("color: #2196F3; font-size: 22px; font-family: 'Times New Roman';")
        self.current_frame = (self.current_frame + 1) % len(self.loading_text)
    
    def show_loading(self, text="加载中..."):
        """显示加载动画"""
        self.text_label.setText(text)
        self.adjustSize()
        
        # 定位到中心
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.center().x() - self.width() // 2
            y = parent_rect.center().y() - self.height() // 2
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
            x = screen_rect.center().x() - self.width() // 2
            y = screen_rect.center().y() - self.height() // 2
        
        self.setGeometry(x, y, self.width(), self.height())
        self.show()
    
    def hide_loading(self):
        """隐藏加载动画"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        self.hide()

class SkeletonWidget(QWidget):
    """骨架屏"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        # 标题骨架
        title_skeleton = QWidget()
        title_skeleton.setFixedHeight(24)
        title_skeleton.setStyleSheet("""QWidget {
            background-color: #E0E0E0;
            border-radius: 4px;
        }""")
        layout.addWidget(title_skeleton)
        
        # 内容骨架
        for i in range(3):
            content_skeleton = QWidget()
            content_skeleton.setFixedHeight(16)
            content_skeleton.setStyleSheet("""QWidget {
                background-color: #E0E0E0;
                border-radius: 4px;
                margin-top: 8px;
            }""")
            layout.addWidget(content_skeleton)
        
        self.setLayout(layout)
        
        # 启动渐变动画
        self._start_animation()
    
    def _start_animation(self):
        """启动渐变动画"""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        self.animation = QPropertyAnimation(self, b"styleSheet")
        self.animation.setDuration(1500)
        self.animation.setStartValue("""QWidget {
            background: linear-gradient(90deg, #E0E0E0 25%, #F0F0F0 50%, #E0E0E0 75%);
            background-size: 200% 100%;
        }""")
        self.animation.setEndValue("""QWidget {
            background: linear-gradient(90deg, #E0E0E0 25%, #F0F0F0 50%, #E0E0E0 75%);
            background-size: 200% 100%;
        }""")
        self.animation.setEasingCurve(QEasingCurve.Type.Linear)
        self.animation.setLoopCount(-1)
        self.animation.start()
    
    def stop_animation(self):
        """停止动画"""
        if self.animation:
            self.animation.stop()

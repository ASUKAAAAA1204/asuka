#!/usr/bin/env python3
"""
登录对话框模块
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QFont, QColor, QPixmap, QLinearGradient

class LoginDialog(QDialog):
    """登录对话框"""
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.setWindowTitle("登录")
        self.setFixedSize(440, 520)
        
        # 设置窗口样式
        self.setStyleSheet(".QDialog {
            background-color: #fafbfc;
            background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
        }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(80, 80)
        # 创建蓝紫渐变背景的Logo
        pixmap = QPixmap(80, 80)
        gradient = QLinearGradient(0, 0, 80, 80)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        painter = QPainter(pixmap)
        painter.setBrush(gradient)
        painter.drawRoundedRect(0, 0, 80, 80, 16, 16)
        # 绘制白色几何图形（十字形，线条更纤细优雅）
        painter.setPen(QPen(QColor("#FFFFFF"), 3))  # 白色细边框
        # 绘制竖线
        painter.drawLine(40, 20, 40, 60)
        # 绘制横线
        painter.drawLine(20, 40, 60, 40)
        painter.end()
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # 标题
        title_label = QLabel("登录")
        title_label.setFont(QFont('微软雅黑', 16, QFont.Weight.Medium))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1f2937;")
        layout.addWidget(title_label)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedHeight(48)
        self.username_input.setStyleSheet(".QLineEdit {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 0 16px;
            font-size: 14px;
            font-family: '微软雅黑', 'Times New Roman';
            background-color: #ffffff;
        }
        .QLineEdit:focus {
            border: 2px solid #8b5cf6;
            outline: none;
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
        }")
        layout.addWidget(self.username_input)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(48)
        self.password_input.setStyleSheet(".QLineEdit {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 0 16px;
            font-size: 14px;
            font-family: '微软雅黑', 'Times New Roman';
            background-color: #ffffff;
        }
        .QLineEdit:focus {
            border: 2px solid #8b5cf6;
            outline: none;
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
        }")
        layout.addWidget(self.password_input)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setFixedHeight(48)
        self.login_button.setStyleSheet("""
            .QPushButton {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-family: '微软雅黑', 'Times New Roman';
                font-weight: 600;
            }
            .QPushButton:hover {
                filter: brightness(1.1);
                transform: translateY(-2px);
            }
            .QPushButton:pressed {
                transform: scale(0.98);
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
            }
        """)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # 注册链接
        self.register_button = QPushButton("注册新账号")
        self.register_button.setFlat(True)
        self.register_button.setStyleSheet("""
            .QPushButton {
                background: transparent;
                color: #6b7280;
                border: none;
                font-size: 14px;
                font-family: '微软雅黑', 'Times New Roman';
            }
            .QPushButton:hover {
                color: #374151;
                background-color: #f3f4f6;
                border-radius: 8px;
            }
        """)
        self.register_button.clicked.connect(self.show_register_dialog)
        layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 状态信息
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #ef4444; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 登录结果
        self.login_result = None
        
        # 初始化动画
        self._init_animation()
        
        # 设置窗口阴影
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(".QDialog {
            background: transparent;
        }")
        
        # 创建带阴影的容器
        from PyQt6.QtWidgets import QWidget
        container = QWidget(self)
        container.setGeometry(10, 10, 420, 500)
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);
            }
        """)
        
        # 重新设置布局到容器
        container.setLayout(layout)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)
    
    def _init_animation(self):
        """初始化动画"""
        # 启动动画
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        
        animation_group = QSequentialAnimationGroup(self)
        
        # Logo动画
        logo_widget = self.layout().itemAt(0).widget().layout().itemAt(0).widget()
        logo_effect = QGraphicsOpacityEffect(logo_widget)
        logo_widget.setGraphicsEffect(logo_effect)
        logo_effect.setOpacity(0)
        logo_anim = QPropertyAnimation(logo_effect, b"opacity")
        logo_anim.setDuration(400)
        logo_anim.setStartValue(0)
        logo_anim.setEndValue(1)
        logo_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 标题动画
        title_widget = self.layout().itemAt(0).widget().layout().itemAt(1).widget()
        title_effect = QGraphicsOpacityEffect(title_widget)
        title_widget.setGraphicsEffect(title_effect)
        title_effect.setOpacity(0)
        title_anim = QPropertyAnimation(title_effect, b"opacity")
        title_anim.setDuration(300)
        title_anim.setStartValue(0)
        title_anim.setEndValue(1)
        title_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 用户名输入框动画
        username_effect = QGraphicsOpacityEffect(self.username_input)
        self.username_input.setGraphicsEffect(username_effect)
        username_effect.setOpacity(0)
        username_anim = QPropertyAnimation(username_effect, b"opacity")
        username_anim.setDuration(300)
        username_anim.setStartValue(0)
        username_anim.setEndValue(1)
        username_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 密码输入框动画
        password_effect = QGraphicsOpacityEffect(self.password_input)
        self.password_input.setGraphicsEffect(password_effect)
        password_effect.setOpacity(0)
        password_anim = QPropertyAnimation(password_effect, b"opacity")
        password_anim.setDuration(300)
        password_anim.setStartValue(0)
        password_anim.setEndValue(1)
        password_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 登录按钮动画
        login_effect = QGraphicsOpacityEffect(self.login_button)
        self.login_button.setGraphicsEffect(login_effect)
        login_effect.setOpacity(0)
        login_anim = QPropertyAnimation(login_effect, b"opacity")
        login_anim.setDuration(300)
        login_anim.setStartValue(0)
        login_anim.setEndValue(1)
        login_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 注册按钮动画
        register_effect = QGraphicsOpacityEffect(self.register_button)
        self.register_button.setGraphicsEffect(register_effect)
        register_effect.setOpacity(0)
        register_anim = QPropertyAnimation(register_effect, b"opacity")
        register_anim.setDuration(300)
        register_anim.setStartValue(0)
        register_anim.setEndValue(1)
        register_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 添加动画到组
        animation_group.addAnimation(logo_anim)
        animation_group.addAnimation(title_anim)
        animation_group.addAnimation(username_anim)
        animation_group.addAnimation(password_anim)
        animation_group.addAnimation(login_anim)
        animation_group.addAnimation(register_anim)
        
        # 启动动画
        animation_group.start()
    
    def login(self):
        """登录处理"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.status_label.setText("请输入用户名和密码")
            return
        
        result = self.user_manager.login(username, password)
        if result['success']:
            self.login_result = result
            self.accept()
        else:
            self.status_label.setText(result['message'])
    
    def show_register_dialog(self):
        """显示注册对话框"""
        from .register_dialog import RegisterDialog
        dialog = RegisterDialog(self.user_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status_label.setText("注册成功，请登录")

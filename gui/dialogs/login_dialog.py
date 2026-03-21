#!/usr/bin/env python3
"""
登录对话框模块
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QFont, QColor, QPixmap

class LoginDialog(QDialog):
    """登录对话框"""
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.setWindowTitle("登录")
        self.setFixedSize(400, 360)
        
        # 设置窗口样式
        self.setStyleSheet(".QDialog {
            background-color: #FFFFFF;
        }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(64, 64)
        # 创建一个简单的Logo（蓝色圆形背景，白色粗边框中空的字母T）
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#2196F3"))
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("#FFFFFF"), 4))  # 白色粗边框
        painter.setFont(QFont("Times New Roman", 30, QFont.Weight.Bold))
        # 绘制中空的T字
        # 绘制竖线
        painter.drawLine(32, 16, 32, 48)
        # 绘制横线
        painter.drawLine(16, 24, 48, 24)
        painter.end()
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # 标题
        title_label = QLabel("登录")
        title_label.setFont(QFont('微软雅黑', 10, QFont.Weight.Medium))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #212121;")
        layout.addWidget(title_label)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet(".QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
        }
        .QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }")
        layout.addWidget(self.username_input)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(".QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
        }
        .QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }")
        layout.addWidget(self.password_input)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setFixedHeight(40)
        self.login_button.setStyleSheet("""
            .QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                font-weight: 500;
            }
            .QPushButton:hover {
                background-color: #1976D2;
            }
            .QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # 注册链接
        self.register_button = QPushButton("注册新账号")
        self.register_button.setFlat(True)
        self.register_button.setStyleSheet("color: #2196F3; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        self.register_button.clicked.connect(self.show_register_dialog)
        layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 状态信息
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #F44336; font-size: 10px; font-family: '微软雅黑', 'Times New Roman';")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 登录结果
        self.login_result = None
        
        # 初始化动画
        self._init_animation()
    
    def _init_animation(self):
        """初始化动画"""
        # 启动动画
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        
        animation_group = QSequentialAnimationGroup(self)
        
        # Logo动画
        logo_widget = self.layout().itemAt(0).widget()
        logo_effect = QGraphicsOpacityEffect(logo_widget)
        logo_widget.setGraphicsEffect(logo_effect)
        logo_effect.setOpacity(0)
        logo_anim = QPropertyAnimation(logo_effect, b"opacity")
        logo_anim.setDuration(400)
        logo_anim.setStartValue(0)
        logo_anim.setEndValue(1)
        logo_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 标题动画
        title_widget = self.layout().itemAt(1).widget()
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

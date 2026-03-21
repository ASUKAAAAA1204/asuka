#!/usr/bin/env python3
"""
注册对话框模块
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class RegisterDialog(QDialog):
    """注册对话框"""
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.setWindowTitle("注册")
        self.setFixedSize(400, 420)
        
        # 设置窗口样式
        self.setStyleSheet("""QDialog {
            background-color: #FFFFFF;
        }""")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("注册新账号")
        title_label.setFont(QFont('微软雅黑', 12, QFont.Weight.Medium))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #212121;")
        layout.addWidget(title_label)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet("""QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        layout.addWidget(self.username_input)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("""QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        layout.addWidget(self.password_input)
        
        # 确认密码输入框
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("请确认密码")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedHeight(40)
        self.confirm_password_input.setStyleSheet("""QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        layout.addWidget(self.confirm_password_input)
        
        # 角色选择
        role_layout = QHBoxLayout()
        role_label = QLabel("角色:")
        role_label.setStyleSheet("color: #757575; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "viewer"])
        self.role_combo.setFixedHeight(40)
        self.role_combo.setStyleSheet("""QComboBox {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 12px;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.setFixedHeight(40)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                font-weight: 500;
                flex: 1;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.register_button.clicked.connect(self.register)
        button_layout.addWidget(self.register_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #212121;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                font-weight: 500;
                flex: 1;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #BDBDBD;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 状态信息
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #F44336; font-size: 10px; font-family: '微软雅黑', 'Times New Roman';")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 初始化动画
        self._init_animation()
    
    def _init_animation(self):
        """初始化动画"""
        # 启动动画
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        
        animation_group = QSequentialAnimationGroup(self)
        
        # 标题动画
        title_widget = self.layout().itemAt(0).widget()
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
        
        # 确认密码输入框动画
        confirm_effect = QGraphicsOpacityEffect(self.confirm_password_input)
        self.confirm_password_input.setGraphicsEffect(confirm_effect)
        confirm_effect.setOpacity(0)
        confirm_anim = QPropertyAnimation(confirm_effect, b"opacity")
        confirm_anim.setDuration(300)
        confirm_anim.setStartValue(0)
        confirm_anim.setEndValue(1)
        confirm_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 角色选择动画
        role_effect = QGraphicsOpacityEffect(self.role_combo)
        self.role_combo.setGraphicsEffect(role_effect)
        role_effect.setOpacity(0)
        role_anim = QPropertyAnimation(role_effect, b"opacity")
        role_anim.setDuration(300)
        role_anim.setStartValue(0)
        role_anim.setEndValue(1)
        role_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 注册按钮动画
        register_effect = QGraphicsOpacityEffect(self.register_button)
        self.register_button.setGraphicsEffect(register_effect)
        register_effect.setOpacity(0)
        register_anim = QPropertyAnimation(register_effect, b"opacity")
        register_anim.setDuration(300)
        register_anim.setStartValue(0)
        register_anim.setEndValue(1)
        register_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 取消按钮动画
        cancel_effect = QGraphicsOpacityEffect(self.cancel_button)
        self.cancel_button.setGraphicsEffect(cancel_effect)
        cancel_effect.setOpacity(0)
        cancel_anim = QPropertyAnimation(cancel_effect, b"opacity")
        cancel_anim.setDuration(300)
        cancel_anim.setStartValue(0)
        cancel_anim.setEndValue(1)
        cancel_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 添加动画到组
        animation_group.addAnimation(title_anim)
        animation_group.addAnimation(username_anim)
        animation_group.addAnimation(password_anim)
        animation_group.addAnimation(confirm_anim)
        animation_group.addAnimation(role_anim)
        animation_group.addAnimation(register_anim)
        animation_group.addAnimation(cancel_anim)
        
        # 启动动画
        animation_group.start()
    
    def register(self):
        """注册处理"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        role = self.role_combo.currentText()
        
        if not username or not password:
            self.status_label.setText("请输入用户名和密码")
            return
        
        if password != confirm_password:
            self.status_label.setText("两次输入的密码不一致")
            return
        
        result = self.user_manager.register(username, password, role)
        if result['success']:
            self.accept()
        else:
            self.status_label.setText(result['message'])

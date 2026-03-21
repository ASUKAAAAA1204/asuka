#!/usr/bin/env python3
"""
本地化智能文件管理系统 - GUI应用
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QTabWidget, QListWidget, QListWidgetItem, QPushButton, QLineEdit, 
    QLabel, QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox, 
    QFileDialog, QComboBox, QCheckBox, QMenu, QToolBar,
    QStatusBar, QProgressBar, QDialog, QFormLayout, QInputDialog,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QTextEdit, QGraphicsOpacityEffect, QScrollArea
)
from PyQt6.QtGui import QAction, QPainter, QPen, QBrush, QFont, QColor
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QCategoryAxis, QValueAxis
import math
from PyQt6.QtCore import Qt, QSize, QThreadPool, QRunnable, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap, QActionGroup

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore
from local_file_manager.modules.file_import.file_importer import FileImporter
from local_file_manager.modules.file_management.file_manager import FileManager
from local_file_manager.modules.search.search_engine import SearchEngine
from local_file_manager.modules.tagging.tag_manager import TagManager
from local_file_manager.modules.knowledge_graph.graph_viewer import GraphViewer
from local_file_manager.modules.user_management.user_manager import UserManager
from local_file_manager.modules.workflow.workflow_manager import WorkflowManager
from local_file_manager.modules.p2p.discovery import P2PDiscovery
from local_file_manager.modules.p2p.communication import P2PServer, P2PClient
from local_file_manager.modules.p2p.group_manager import GroupManager

class LoginDialog(QDialog):
    """登录对话框"""
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.setWindowTitle("登录")
        self.setFixedSize(400, 360)
        
        # 设置窗口样式
        self.setStyleSheet(""".QDialog {
            background-color: #FFFFFF;
        }""")
        
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
        self.username_input.setStyleSheet(""".QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
        }
        .QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        layout.addWidget(self.username_input)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(""".QLineEdit {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
        }
        .QLineEdit:focus {
            border-color: #2196F3;
            outline: none;
        }""")
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
        dialog = RegisterDialog(self.user_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status_label.setText("注册成功，请登录")

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

class UserManagementWidget(QWidget):
    """用户管理控件"""
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("用户管理")
        title_label.setFont(QFont('微软雅黑', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 用户列表
        self.user_list = QListWidget()
        self.user_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.user_list.customContextMenuRequested.connect(self.show_user_context_menu)
        layout.addWidget(self.user_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_users)
        button_layout.addWidget(refresh_button)
        
        add_user_button = QPushButton("添加用户")
        add_user_button.clicked.connect(self.add_user)
        button_layout.addWidget(add_user_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.refresh_users()
    
    def refresh_users(self):
        """刷新用户列表"""
        users = self.user_manager.get_users()
        self.user_list.clear()
        for user in users:
            item = QListWidgetItem(f"{user['username']} (角色: {user['role']})")
            item.setData(Qt.ItemDataRole.UserRole, user)
            self.user_list.addItem(item)
    
    def show_user_context_menu(self, pos):
        """显示用户上下文菜单"""
        item = self.user_list.itemAt(pos)
        if not item:
            return
        
        user = item.data(Qt.ItemDataRole.UserRole)
        if not user:
            return
        
        menu = QMenu()
        
        edit_role_action = QAction("修改角色", self)
        edit_role_action.triggered.connect(lambda: self.edit_user_role(user))
        menu.addAction(edit_role_action)
        
        change_password_action = QAction("修改密码", self)
        change_password_action.triggered.connect(lambda: self.change_user_password(user))
        menu.addAction(change_password_action)
        
        delete_action = QAction("删除用户", self)
        delete_action.triggered.connect(lambda: self.delete_user(user))
        menu.addAction(delete_action)
        
        menu.exec(self.user_list.mapToGlobal(pos))
    
    def add_user(self):
        """添加用户"""
        dialog = RegisterDialog(self.user_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_users()
    
    def edit_user_role(self, user):
        """修改用户角色"""
        dialog = QDialog(self)
        dialog.setWindowTitle("修改角色")
        dialog.resize(300, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"用户: {user['username']}"))
        
        role_label = QLabel("新角色:")
        layout.addWidget(role_label)
        
        role_combo = QComboBox()
        role_combo.addItems(["admin", "user", "viewer"])
        role_combo.setCurrentText(user['role'])
        layout.addWidget(role_combo)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def on_ok():
            new_role = role_combo.currentText()
            result = self.user_manager.update_user_role(user['id'], new_role)
            if result['success']:
                QMessageBox.information(self, "成功", "角色更新成功")
                self.refresh_users()
                dialog.accept()
            else:
                QMessageBox.warning(self, "失败", result['message'])
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def change_user_password(self, user):
        """修改用户密码"""
        dialog = QDialog(self)
        dialog.setWindowTitle("修改密码")
        dialog.resize(300, 200)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"用户: {user['username']}"))
        
        old_password_label = QLabel("旧密码:")
        layout.addWidget(old_password_label)
        old_password_input = QLineEdit()
        old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(old_password_input)
        
        new_password_label = QLabel("新密码:")
        layout.addWidget(new_password_label)
        new_password_input = QLineEdit()
        new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(new_password_input)
        
        confirm_password_label = QLabel("确认新密码:")
        layout.addWidget(confirm_password_label)
        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(confirm_password_input)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def on_ok():
            old_password = old_password_input.text()
            new_password = new_password_input.text()
            confirm_password = confirm_password_input.text()
            
            if not old_password or not new_password:
                QMessageBox.warning(self, "警告", "请输入旧密码和新密码")
                return
            
            if new_password != confirm_password:
                QMessageBox.warning(self, "警告", "两次输入的新密码不一致")
                return
            
            result = self.user_manager.change_password(user['id'], old_password, new_password)
            if result['success']:
                QMessageBox.information(self, "成功", "密码修改成功")
                dialog.accept()
            else:
                QMessageBox.warning(self, "失败", result['message'])
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def delete_user(self, user):
        """删除用户"""
        reply = QMessageBox.question(self, "确认删除", f"确定要删除用户 {user['username']} 吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.user_manager.delete_user(user['id'])
            if result['success']:
                QMessageBox.information(self, "成功", "用户删除成功")
                self.refresh_users()
            else:
                QMessageBox.warning(self, "失败", result['message'])

class WorkerSignals(QObject):
    """工作信号类"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):
    """工作线程类"""
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

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

class FileItemWidget(QWidget):
    """文件项控件"""
    def __init__(self, file_info, file_manager=None):
        super().__init__()
        self.file_info = file_info
        self.file_manager = file_manager
        
        # 透明度效果
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

class SearchWidget(QWidget):
    """搜索控件"""
    def __init__(self, search_engine):
        super().__init__()
        self.search_engine = search_engine
        
        # 设置背景样式
        self.setStyleSheet("""QWidget {
            background-color: #F8F9FA;
        }""")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 搜索输入区
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索关键词...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                height: 40px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                outline: none;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        # 搜索按钮
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                font-size: 10px;
                font-family: '微软雅黑', 'Times New Roman';
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        search_layout.addWidget(self.search_button)
        
        # 搜索类型
        self.search_type = QComboBox()
        self.search_type.addItems(["关键词搜索", "语义搜索", "关联搜索", "内容搜索"])
        self.search_type.setStyleSheet("""QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            height: 40px;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        search_layout.addWidget(self.search_type)
        
        layout.addLayout(search_layout)
        
        # 搜索过滤器
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(16)
        
        filter_label = QLabel("过滤:")
        filter_label.setStyleSheet("color: #757575; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        filter_layout.addWidget(filter_label)
        
        self.file_type_filter = QComboBox()
        self.file_type_filter.addItems(["所有类型", "文本", "PDF", "图片", "视频", "音频", "Office"])
        self.file_type_filter.setStyleSheet("""QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 0 8px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            height: 32px;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        filter_layout.addWidget(self.file_type_filter)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["所有分类", "技术文档", "研究资料", "学习资料", "工作文档", "个人资料"])
        self.category_filter.setStyleSheet("""QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 0 8px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            height: 32px;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        filter_layout.addWidget(self.category_filter)
        
        self.sort_by = QComboBox()
        self.sort_by.addItems(["相关性", "创建时间", "文件名"])
        self.sort_by.setStyleSheet("""QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 0 8px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            height: 32px;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        filter_layout.addWidget(self.sort_by)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 搜索结果
        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.open_file)
        self.result_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background-color: #F0F2F5;
        }""")
        layout.addWidget(self.result_list)
        
        # 搜索历史
        history_layout = QHBoxLayout()
        history_layout.setSpacing(12)
        
        history_label = QLabel("搜索历史:")
        history_label.setStyleSheet("color: #757575; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        history_layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        self.history_list.itemClicked.connect(self.load_history)
        self.history_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px;
        }
        QListWidget::item {
            padding: 4px 8px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background-color: #F0F2F5;
        }""")
        history_layout.addWidget(self.history_list)
        
        clear_history_button = QPushButton("清空历史")
        clear_history_button.clicked.connect(self.clear_history)
        clear_history_button.setStyleSheet("""QPushButton {
            background-color: #F5F5F5;
            color: #757575;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
        }
        QPushButton:hover {
            background-color: #E0E0E0;
        }""")
        history_layout.addWidget(clear_history_button)
        
        layout.addLayout(history_layout)
        
        self.setLayout(layout)
        self.load_search_history()
        
        # 连接过滤器信号
        self.file_type_filter.currentIndexChanged.connect(self.perform_search)
        self.category_filter.currentIndexChanged.connect(self.perform_search)
        self.sort_by.currentIndexChanged.connect(self.perform_search)
    
    def perform_search(self):
        """执行搜索"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        search_type_map = {
            "关键词搜索": "keyword",
            "语义搜索": "semantic",
            "关联搜索": "related",
            "内容搜索": "content"
        }
        search_type = search_type_map[self.search_type.currentText()]
        
        # 构建搜索参数
        search_kwargs = {
            'search_type': search_type
        }
        
        # 应用文件类型过滤器
        file_type = self.file_type_filter.currentText()
        if file_type != "所有类型":
            file_type_map = {
                "文本": "text",
                "PDF": "pdf",
                "图片": "image",
                "视频": "video",
                "音频": "audio",
                "Office": "office"
            }
            search_kwargs['file_types'] = [file_type_map.get(file_type, file_type)]
        
        # 应用分类过滤器
        category = self.category_filter.currentText()
        if category != "所有分类":
            search_kwargs['categories'] = [category]
        
        # 执行搜索
        pool = QThreadPool.globalInstance()
        worker = Worker(self.search_engine.search, query, **search_kwargs)
        worker.signals.result.connect(self.display_results)
        pool.start(worker)
    
    def display_results(self, results):
        """显示搜索结果"""
        # 应用排序
        sort_by = self.sort_by.currentText()
        if sort_by == "相关性":
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
        elif sort_by == "创建时间":
            results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == "文件名":
            results.sort(key=lambda x: x.get('filename', ''))
        
        # 显示结果
        self.result_list.clear()
        
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        
        animation_group = QSequentialAnimationGroup(self)
        
        for i, result in enumerate(results):
            item = QListWidgetItem()
            widget = FileItemWidget(result)
            widget.setFixedHeight(100)
            widget.setOpacity(0)  # 初始设置为透明
            
            item.setSizeHint(widget.sizeHint())
            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, widget)
            
            # 添加延迟（除了第一个元素）
            if i > 0:
                animation_group.addPause(50)
            
            # 创建淡入动画
            anim = QPropertyAnimation(widget.opacity_effect, b"opacity")
            anim.setDuration(300)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation_group.addAnimation(anim)
        
        # 启动动画
        animation_group.start()
    
    def open_file(self, item):
        """打开文件"""
        widget = self.result_list.itemWidget(item)
        if widget:
            widget.open_file()
    
    def load_search_history(self):
        """加载搜索历史"""
        history = self.search_engine.get_search_history()
        self.history_list.clear()
        for item in history:
            self.history_list.addItem(item)
    
    def load_history(self, item):
        """加载历史搜索"""
        self.search_input.setText(item.text())
        self.perform_search()
    
    def clear_history(self):
        """清空搜索历史"""
        self.search_engine.clear_search_history()
        self.history_list.clear()

class FileManagementWidget(QWidget):
    """文件管理控件"""
    def __init__(self, file_manager, file_importer):
        super().__init__()
        self.file_manager = file_manager
        self.file_importer = file_importer
        
        # 设置背景样式
        self.setStyleSheet("""QWidget {
            background-color: #F8F9FA;
        }""")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 工具栏
        toolbar = QToolBar()
        toolbar.setStyleSheet("""QToolBar {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 8px;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
        }
        QPushButton:hover {
            background-color: #1976D2;
        }""")
        
        import_action = QPushButton("导入文件")
        import_action.clicked.connect(self.import_file)
        toolbar.addWidget(import_action)
        
        refresh_action = QPushButton("刷新")
        refresh_action.clicked.connect(self.refresh_files)
        toolbar.addWidget(refresh_action)
        
        layout.addWidget(toolbar)
        
        # 分类筛选和视图切换
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(16)
        
        # 分类筛选
        category_label = QLabel("分类:")
        category_label.setStyleSheet("color: #757575; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        filter_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("所有分类")
        self.category_combo.addItems(["技术文档", "研究资料", "学习资料", "工作文档", "个人资料"])
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        self.category_combo.setStyleSheet("""QComboBox {
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            background-color: #FFFFFF;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addStretch()
        
        # 视图切换
        view_label = QLabel("视图:")
        view_label.setStyleSheet("color: #757575; font-size: 12px; font-family: '微软雅黑', 'Times New Roman';")
        filter_layout.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["网格视图", "列表视图"])
        self.view_combo.currentTextChanged.connect(self.refresh_files)
        self.view_combo.setStyleSheet("""QComboBox {
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            background-color: #FFFFFF;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        filter_layout.addWidget(self.view_combo)
        
        layout.addLayout(filter_layout)
        
        # 文件列表容器
        self.file_container = QWidget()
        self.file_layout = QGridLayout(self.file_container)
        self.file_layout.setSpacing(16)
        self.file_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.file_container)
        scroll_area.setStyleSheet("""QScrollArea {
            border: none;
            background-color: transparent;
        }""")
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        self.refresh_files()
        
        # 启用拖放功能
        self.setAcceptDrops(True)
    
    def refresh_files(self):
        """刷新文件列表"""
        category = self.category_combo.currentText()
        if category == "所有分类":
            files = self.file_manager.get_files()
        else:
            files = self.file_manager.get_files(category=category)
        
        # 清空当前布局
        while self.file_layout.count() > 0:
            item = self.file_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 获取当前视图模式
        view_mode = self.view_combo.currentText()
        
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        
        animation_group = QSequentialAnimationGroup(self)
        
        if view_mode == "网格视图":
            # 网格视图布局
            row = 0
            col = 0
            
            # 根据窗口宽度动态调整列数
            container_width = self.file_container.width()
            card_width = 240
            max_cols = max(1, container_width // (card_width + 16))  # 16是间距
            
            for i, file in enumerate(files):
                widget = FileItemWidget(file, self.file_manager)
                widget.setFixedSize(240, 180)
                widget.setOpacity(0)  # 初始设置为透明
                self.file_layout.addWidget(widget, row, col)
                
                # 连接信号
                widget.mousePressEvent = lambda event, f=file: self.open_file(f)
                
                # 添加延迟（除了第一个元素）
                if i > 0:
                    animation_group.addPause(50)
                
                # 创建淡入动画
                anim = QPropertyAnimation(widget.opacity_effect, b"opacity")
                anim.setDuration(300)
                anim.setStartValue(0)
                anim.setEndValue(1)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation_group.addAnimation(anim)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        else:
            # 列表视图布局
            for i, file in enumerate(files):
                widget = FileItemWidget(file, self.file_manager)
                widget.setFixedHeight(100)
                widget.setOpacity(0)  # 初始设置为透明
                self.file_layout.addWidget(widget)
                
                # 连接信号
                widget.mousePressEvent = lambda event, f=file: self.open_file(f)
                
                # 添加延迟（除了第一个元素）
                if i > 0:
                    animation_group.addPause(50)
                
                # 创建淡入动画
                anim = QPropertyAnimation(widget.opacity_effect, b"opacity")
                anim.setDuration(300)
                anim.setStartValue(0)
                anim.setEndValue(1)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation_group.addAnimation(anim)
        
        # 启动动画
        animation_group.start()
    
    def resizeEvent(self, event):
        """窗口大小变化事件处理"""
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 重新刷新文件列表，以适应新的窗口大小
        if self.view_combo.currentText() == "网格视图":
            self.refresh_files()
    
    def filter_by_category(self):
        """按分类筛选"""
        self.refresh_files()
    
    def import_file(self):
        """导入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt);;PDF文件 (*.pdf);;图片文件 (*.jpg *.png)"
        )
        if file_path:
            # 显示加载动画
            main_window = self.window()
            if hasattr(main_window, 'loading'):
                main_window.loading.show_loading("导入文件中...")
            
            pool = QThreadPool.globalInstance()
            worker = Worker(self.file_importer.import_file, file_path)
            worker.signals.result.connect(lambda result: self.import_result(result, main_window))
            worker.signals.error.connect(lambda error: self.import_error(error, main_window))
            pool.start(worker)
    
    def import_result(self, result, main_window=None):
        """导入结果"""
        # 隐藏加载动画
        if main_window and hasattr(main_window, 'loading'):
            main_window.loading.hide_loading()
        
        if result['success']:
            # 获取主窗口的Toast通知实例
            if main_window and hasattr(main_window, 'toast'):
                main_window.toast.show_notification(f"文件导入成功\n文件ID: {result['file_id']}\n分类: {result['category']}", "success")
            self.refresh_files()
        else:
            # 获取主窗口的Toast通知实例
            if main_window and hasattr(main_window, 'toast'):
                main_window.toast.show_notification(f"文件导入失败: {result['message']}", "error")
    
    def import_error(self, error, main_window=None):
        """导入错误"""
        # 隐藏加载动画
        if main_window and hasattr(main_window, 'loading'):
            main_window.loading.hide_loading()
        
        # 获取主窗口的Toast通知实例
        if main_window and hasattr(main_window, 'toast'):
            main_window.toast.show_notification(f"导入过程中发生错误: {error}", "error")
    
    def open_file(self, file_info):
        """打开文件"""
        if file_info and 'file_path' in file_info:
            file_path = file_info['file_path']
            if os.path.exists(file_path):
                os.startfile(file_path) if sys.platform == 'win32' else os.system(f'open "{file_path}"')
    

    


class TagManagementWidget(QWidget):
    """标签管理控件"""
    def __init__(self, tag_manager, file_manager):
        super().__init__()
        self.tag_manager = tag_manager
        self.file_manager = file_manager
        
        # 设置背景样式
        self.setStyleSheet("""QWidget {
            background-color: #F8F9FA;
        }""")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标签列表和操作
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""QSplitter {
            background-color: #F8F9FA;
        }
        QSplitter::handle {
            background-color: #E0E0E0;
            width: 1px;
        }""")
        
        # 左侧标签列表
        tag_list_widget = QWidget()
        tag_list_layout = QVBoxLayout()
        tag_list_layout.setContentsMargins(0, 0, 0, 0)
        tag_list_layout.setSpacing(12)
        
        tag_label = QLabel("所有标签:")
        tag_label.setStyleSheet("color: #757575; font-size: 14px;")
        tag_list_layout.addWidget(tag_label)
        
        self.tag_list = QListWidget()
        self.tag_list.itemClicked.connect(self.select_tag)
        self.tag_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #F0F2F5;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        tag_list_layout.addWidget(self.tag_list)
        
        tag_buttons_layout = QHBoxLayout()
        tag_buttons_layout.setSpacing(12)
        
        add_tag_button = QPushButton("添加标签")
        add_tag_button.clicked.connect(self.add_tag)
        add_tag_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        tag_buttons_layout.addWidget(add_tag_button)
        
        delete_tag_button = QPushButton("删除标签")
        delete_tag_button.clicked.connect(self.delete_tag)
        delete_tag_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #757575;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #BDBDBD;
            }
        """)
        tag_buttons_layout.addWidget(delete_tag_button)
        
        tag_list_layout.addLayout(tag_buttons_layout)
        tag_list_widget.setLayout(tag_list_layout)
        
        # 右侧文件列表
        file_list_widget = QWidget()
        file_list_layout = QVBoxLayout()
        file_list_layout.setContentsMargins(0, 0, 0, 0)
        file_list_layout.setSpacing(12)
        
        file_label = QLabel("标签关联的文件:")
        file_label.setStyleSheet("color: #757575; font-size: 14px;")
        file_list_layout.addWidget(file_label)
        
        self.tag_file_list = QListWidget()
        self.tag_file_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background-color: #F0F2F5;
        }""")
        file_list_layout.addWidget(self.tag_file_list)
        
        file_buttons_layout = QHBoxLayout()
        file_buttons_layout.setSpacing(12)
        
        add_file_to_tag_button = QPushButton("添加文件到标签")
        add_file_to_tag_button.clicked.connect(self.add_file_to_tag)
        add_file_to_tag_button.setStyleSheet("""QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
            font-size: 12px;
            transition: all 0.2s ease;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            transform: scale(0.98);
        }""")
        file_buttons_layout.addWidget(add_file_to_tag_button)
        
        remove_file_from_tag_button = QPushButton("从标签移除文件")
        remove_file_from_tag_button.clicked.connect(self.remove_file_from_tag)
        remove_file_from_tag_button.setStyleSheet("""QPushButton {
            background-color: #F5F5F5;
            color: #757575;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 6px 16px;
            font-size: 12px;
            transition: all 0.2s ease;
        }
        QPushButton:hover {
            background-color: #E0E0E0;
        }
        QPushButton:pressed {
            transform: scale(0.98);
        }""")
        file_buttons_layout.addWidget(remove_file_from_tag_button)
        
        file_list_layout.addLayout(file_buttons_layout)
        file_list_widget.setLayout(file_list_layout)
        
        splitter.addWidget(tag_list_widget)
        splitter.addWidget(file_list_widget)
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        self.refresh_tags()
    
    def refresh_tags(self):
        """刷新标签列表"""
        tags = self.tag_manager.get_all_tags()
        self.tag_list.clear()
        
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        
        animation_group = QSequentialAnimationGroup(self)
        
        for i, tag in enumerate(tags):
            item = QListWidgetItem(tag)
            self.tag_list.addItem(item)
            
            # 获取项的widget
            widget = self.tag_list.itemWidget(item)
            if not widget:
                # 如果没有widget，创建一个
                widget = QLabel(tag)
                widget.setStyleSheet("padding: 8px 12px;")
                # 添加透明度效果
                opacity_effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(opacity_effect)
                opacity_effect.setOpacity(0)  # 初始设置为透明
                widget.opacity_effect = opacity_effect  # 存储引用
                self.tag_list.setItemWidget(item, widget)
            else:
                # 确保widget有opacity_effect
                if hasattr(widget, 'opacity_effect'):
                    widget.opacity_effect.setOpacity(0)
            
            # 添加延迟（除了第一个元素）
            if i > 0:
                animation_group.addPause(50)
            
            # 创建淡入动画
            if hasattr(widget, 'opacity_effect'):
                anim = QPropertyAnimation(widget.opacity_effect, b"opacity")
                anim.setDuration(300)
                anim.setStartValue(0)
                anim.setEndValue(1)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation_group.addAnimation(anim)
        
        # 启动动画
        animation_group.start()
    
    def select_tag(self, item):
        """选择标签"""
        tag_name = item.text()
        # 获取包含此标签的文件
        files = self.file_manager.get_files()
        tag_files = []
        for file in files:
            file_tags = self.tag_manager.get_file_tags(file['id'])
            if tag_name in file_tags:
                tag_files.append(file)
        
        self.tag_file_list.clear()
        
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        
        animation_group = QSequentialAnimationGroup(self)
        
        for i, file in enumerate(tag_files):
            item = QListWidgetItem()
            widget = FileItemWidget(file, self.file_manager)
            widget.setFixedHeight(100)
            widget.setOpacity(0)  # 初始设置为透明
            
            item.setSizeHint(widget.sizeHint())
            self.tag_file_list.addItem(item)
            self.tag_file_list.setItemWidget(item, widget)
            
            # 创建淡入动画
            anim = QPropertyAnimation(widget, b"opacity")
            anim.setDuration(300)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setDelay(i * 50)  # 每个文件延迟50ms，创建逐个出现的效果
            
            animation_group.addAnimation(anim)
        
        # 启动动画
        animation_group.start()
    
    def add_tag(self):
        """添加标签"""
        tag_name, ok = QInputDialog.getText(self, "添加标签", "请输入标签名称:")
        if ok and tag_name:
            result = self.tag_manager.add_tag(tag_name)
            if result['success']:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification("标签添加成功", "success")
                self.refresh_tags()
            else:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification(f"标签添加失败: {result['message']}", "error")
    
    def delete_tag(self):
        """删除标签"""
        selected_item = self.tag_list.currentItem()
        if not selected_item:
            # 获取主窗口的Toast通知实例
            main_window = self.window()
            if hasattr(main_window, 'toast'):
                main_window.toast.show_notification("请选择要删除的标签", "warning")
            return
        
        tag_name = selected_item.text()
        reply = QMessageBox.question(self, "确认删除", f"确定要删除标签 {tag_name} 吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.tag_manager.remove_tag(tag_name)
            if result['success']:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification("标签删除成功", "success")
                self.refresh_tags()
                self.tag_file_list.clear()
            else:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification(f"标签删除失败: {result['message']}", "error")
    
    def add_file_to_tag(self):
        """添加文件到标签"""
        selected_tag = self.tag_list.currentItem()
        if not selected_tag:
            # 获取主窗口的Toast通知实例
            main_window = self.window()
            if hasattr(main_window, 'toast'):
                main_window.toast.show_notification("请选择一个标签", "warning")
            return
        
        tag_name = selected_tag.text()
        
        # 显示文件选择对话框
        files = self.file_manager.get_files()
        file_names = [f"{file['filename']} (ID: {file['id']})".ljust(50) + f"分类: {file.get('category', '未分类')}" for file in files]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("选择文件")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        list_widget.addItems(file_names)
        layout.addWidget(list_widget)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        selected_files = []
        def on_ok():
            for item in list_widget.selectedItems():
                index = list_widget.row(item)
                selected_files.append(files[index])
            dialog.accept()
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and selected_files:
            for file in selected_files:
                result = self.tag_manager.add_tags_to_file(file['id'], [tag_name])
                if not result['success']:
                    # 获取主窗口的Toast通知实例
                    main_window = self.window()
                    if hasattr(main_window, 'toast'):
                        main_window.toast.show_notification(f"添加文件到标签失败: {result['message']}", "error")
                    return
            # 获取主窗口的Toast通知实例
            main_window = self.window()
            if hasattr(main_window, 'toast'):
                main_window.toast.show_notification("文件添加到标签成功", "success")
            self.select_tag(selected_tag)
    
    def remove_file_from_tag(self):
        """从标签移除文件"""
        selected_tag = self.tag_list.currentItem()
        if not selected_tag:
            # 获取主窗口的Toast通知实例
            main_window = self.window()
            if hasattr(main_window, 'toast'):
                main_window.toast.show_notification("请选择一个标签", "warning")
            return
        
        selected_item = self.tag_file_list.currentItem()
        if not selected_item:
            # 获取主窗口的Toast通知实例
            main_window = self.window()
            if hasattr(main_window, 'toast'):
                main_window.toast.show_notification("请选择要移除的文件", "warning")
            return
        
        tag_name = selected_tag.text()
        widget = self.tag_file_list.itemWidget(selected_item)
        if widget:
            file_id = widget.file_info['id']
            result = self.tag_manager.remove_tags_from_file(file_id, [tag_name])
            if result['success']:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification("文件从标签移除成功", "success")
                self.select_tag(selected_tag)
            else:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification(f"从标签移除文件失败: {result['message']}", "error")

class GraphView(QGraphicsView):
    """图谱视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setMinimumSize(800, 600)
        
        # 存储节点和边的引用
        self.nodes = {}
        self.edges = {}
        
    def wheelEvent(self, event):
        """鼠标滚轮事件，实现缩放"""
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)
    
    def draw_graph(self, graph_data):
        """绘制图谱"""
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # 计算布局
        node_positions = self._calculate_layout(nodes)
        
        # 绘制边
        for edge in edges:
            source_id = edge['source']
            target_id = edge['target']
            if source_id in node_positions and target_id in node_positions:
                source_pos = node_positions[source_id]
                target_pos = node_positions[target_id]
                
                # 根据相似度设置边的粗细和颜色
                similarity = edge.get('similarity', 0.5)
                pen_width = 1 + similarity * 2
                pen_color = QColor(100, 100, 255, int(similarity * 200 + 55))
                
                line = QGraphicsLineItem(source_pos.x(), source_pos.y(), target_pos.x(), target_pos.y())
                line.setPen(QPen(pen_color, pen_width))
                self.scene.addItem(line)
                
                # 存储边的引用
                edge_key = f"{source_id}-{target_id}"
                self.edges[edge_key] = line
        
        # 绘制节点
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
        
        animation_group = QSequentialAnimationGroup(self)
        
        for i, node in enumerate(nodes):
            node_id = node['id']
            if node_id in node_positions:
                pos = node_positions[node_id]
                circle, text = self._draw_node(node, pos)
                
                # 存储节点的引用
                self.nodes[node_id] = {
                    'circle': circle,
                    'text': text,
                    'pos': pos,
                    'file_type': node.get('file_type', '').lower()
                }
                
                # 创建节点动画
                # 初始位置在中心
                center_pos = QPointF(0, 0)
                circle.setPos(center_pos)
                text.setPos(center_pos.x() + 25, center_pos.y() - 10)
                
                # 添加延迟（除了第一个元素）
                if i > 0:
                    animation_group.addPause(30)
                
                # 位置动画
                pos_anim = QPropertyAnimation(circle, b"pos")
                pos_anim.setDuration(800)
                pos_anim.setStartValue(center_pos)
                pos_anim.setEndValue(pos)
                pos_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
                animation_group.addAnimation(pos_anim)
                
                # 透明度动画
                circle.setOpacity(0)
                opacity_anim = QPropertyAnimation(circle, b"opacity")
                opacity_anim.setDuration(400)
                opacity_anim.setStartValue(0)
                opacity_anim.setEndValue(1)
                animation_group.addAnimation(opacity_anim)
                
                # 文本位置动画
                text_pos_anim = QPropertyAnimation(text, b"pos")
                text_pos_anim.setDuration(800)
                text_pos_anim.setStartValue(QPointF(center_pos.x() + 25, center_pos.y() - 10))
                text_pos_anim.setEndValue(QPointF(pos.x() + 25, pos.y() - 10))
                text_pos_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
                animation_group.addAnimation(text_pos_anim)
                
                # 文本动画（延迟200ms）
                animation_group.addPause(200)
                text.setOpacity(0)
                text_anim = QPropertyAnimation(text, b"opacity")
                text_anim.setDuration(400)
                text_anim.setStartValue(0)
                text_anim.setEndValue(1)
                animation_group.addAnimation(text_anim)
        
        # 启动动画
        animation_group.start()
        
        # 调整视图
        if nodes:
            # 延迟调整视图，等待动画完成
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self._adjust_view(nodes))
    
    def _adjust_view(self, nodes):
        """调整视图"""
        if nodes:
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _calculate_layout(self, nodes):
        """计算节点布局"""
        positions = {}
        radius = 300
        count = len(nodes)
        
        for i, node in enumerate(nodes):
            angle = 2 * 3.14159 * i / count
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[node['id']] = QPointF(x, y)
        
        return positions
    
    def _draw_node(self, node, pos):
        """绘制节点"""
        # 根据文件类型设置节点颜色
        file_type = node.get('file_type', '').lower()
        if file_type == 'pdf':
            color = QColor('#FF5733')
        elif file_type == 'office':
            color = QColor('#33FF57')
        elif file_type == 'text':
            color = QColor('#3357FF')
        elif file_type == 'image':
            color = QColor('#F3FF33')
        elif file_type == 'video':
            color = QColor('#FF33F3')
        elif file_type == 'audio':
            color = QColor('#33FFF3')
        else:
            color = QColor('#999999')
        
        # 绘制节点圆圈
        circle = QGraphicsEllipseItem(-20, -20, 40, 40)
        circle.setPos(pos)
        circle.setBrush(QBrush(color))
        circle.setPen(QPen(Qt.GlobalColor.black, 1))
        
        # 添加悬停效果
        circle.setToolTip(f"{node['label']}\n分类: {node['category']}\n文件类型: {file_type}")
        
        # 绘制节点标签
        text = QGraphicsTextItem(node['label'])
        text.setPos(pos.x() + 25, pos.y() - 10)
        text.setFont(QFont('Times New Roman', 6))
        
        self.scene.addItem(circle)
        self.scene.addItem(text)
        
        # 添加鼠标事件
        circle.setAcceptHoverEvents(True)
        circle.hoverEnterEvent = lambda event, c=circle: self._on_node_hover_enter(c)
        circle.hoverLeaveEvent = lambda event, c=circle: self._on_node_hover_leave(c)
        circle.mousePressEvent = lambda event, n=node: self._on_node_click(n)
        
        return circle, text
    
    def _on_node_hover_enter(self, circle):
        """节点悬停进入事件"""
        from PyQt6.QtCore import QPropertyAnimation
        
        # 节点放大动画
        scale_anim = QPropertyAnimation(circle, b"scale")
        scale_anim.setDuration(200)
        scale_anim.setStartValue(1.0)
        scale_anim.setEndValue(1.2)
        scale_anim.start()
        
        # 节点阴影加深
        # 这里简化处理，实际可以通过设置更复杂的样式来实现
        circle.setPen(QPen(Qt.GlobalColor.black, 2))
    
    def _on_node_hover_leave(self, circle):
        """节点悬停离开事件"""
        from PyQt6.QtCore import QPropertyAnimation
        
        # 节点恢复动画
        scale_anim = QPropertyAnimation(circle, b"scale")
        scale_anim.setDuration(200)
        scale_anim.setStartValue(1.2)
        scale_anim.setEndValue(1.0)
        scale_anim.start()
        
        # 节点阴影恢复
        circle.setPen(QPen(Qt.GlobalColor.black, 1))
    
    def _on_node_click(self, node):
        """节点点击事件"""
        # 找到对应的节点图形
        node_id = node['id']
        if node_id in self.nodes:
            circle = self.nodes[node_id]['circle']
            
            # 节点脉冲动画
            from PyQt6.QtCore import QPropertyAnimation, QSequentialAnimationGroup
            
            pulse_group = QSequentialAnimationGroup(self)
            
            for i in range(2):
                # 放大
                scale_anim1 = QPropertyAnimation(circle, b"scale")
                scale_anim1.setDuration(200)
                scale_anim1.setStartValue(1.0)
                scale_anim1.setEndValue(1.3)
                
                # 缩小
                scale_anim2 = QPropertyAnimation(circle, b"scale")
                scale_anim2.setDuration(200)
                scale_anim2.setStartValue(1.3)
                scale_anim2.setEndValue(1.0)
                
                pulse_group.addAnimation(scale_anim1)
                pulse_group.addAnimation(scale_anim2)
            
            pulse_group.start()
            
            # 高亮相关节点和边
            # 这里可以根据实际需求实现相关节点的高亮逻辑

class KnowledgeGraphWidget(QWidget):
    """知识图谱控件"""
    def __init__(self, graph_viewer, file_manager):
        super().__init__()
        self.graph_viewer = graph_viewer
        self.file_manager = file_manager
        
        # 设置背景样式
        self.setStyleSheet("""QWidget {
            background-color: #F8F9FA;
        }""")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 图谱控制
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        self.graph_type = QComboBox()
        self.graph_type.addItems(["最近文件图谱", "整个图谱", "以指定文件为中心"])
        self.graph_type.setStyleSheet("""QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 12px;
            height: 40px;
        }
        QComboBox:focus {
            border-color: #2196F3;
            outline: none;
        }""")
        control_layout.addWidget(self.graph_type)
        
        generate_button = QPushButton("生成图谱")
        generate_button.clicked.connect(self.generate_graph)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                font-size: 12px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        control_layout.addWidget(generate_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 图谱显示区域
        self.graph_view = GraphView()
        self.graph_view.setStyleSheet("""QGraphicsView {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
        }""")
        layout.addWidget(self.graph_view)
        
        # 图谱信息
        self.graph_info = QLabel("图谱信息:")
        self.graph_info.setStyleSheet("""QLabel {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
            color: #212121;
        }""")
        layout.addWidget(self.graph_info)
        
        self.setLayout(layout)
    
    def generate_graph(self):
        """生成图谱"""
        graph_type = self.graph_type.currentText()
        
        if graph_type == "最近文件图谱":
            graph_data = self.graph_viewer.generate_graph()
        elif graph_type == "整个图谱":
            graph_data = self.graph_viewer.generate_graph(include_all=True)
        else:  # 以指定文件为中心
            # 显示文件选择对话框
            files = self.file_manager.get_files()
            if not files:
                QMessageBox.warning(self, "警告", "没有文件可选择")
                return
            
            file_names = [f"{file['filename']} (ID: {file['id']})".ljust(50) + f"分类: {file.get('category', '未分类')}" for file in files]
            
            dialog = QDialog(self)
            dialog.setWindowTitle("选择中心文件")
            dialog.resize(600, 400)
            
            layout = QVBoxLayout()
            
            list_widget = QListWidget()
            list_widget.addItems(file_names)
            layout.addWidget(list_widget)
            
            button_layout = QHBoxLayout()
            ok_button = QPushButton("确定")
            cancel_button = QPushButton("取消")
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            selected_file = None
            def on_ok():
                nonlocal selected_file
                if list_widget.currentItem():
                    index = list_widget.row(list_widget.currentItem())
                    selected_file = files[index]
                dialog.accept()
            
            ok_button.clicked.connect(on_ok)
            cancel_button.clicked.connect(dialog.reject)
            
            if dialog.exec() != QDialog.DialogCode.Accepted or not selected_file:
                return
            
            graph_data = self.graph_viewer.generate_graph(file_id=selected_file['id'])
        
        # 显示图谱信息
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        info_text = f"图谱信息: 节点数量 = {len(nodes)}, 边数量 = {len(edges)}\n"
        info_text += "节点类型分布:\n"
        
        type_count = {}
        for node in nodes:
            node_type = node.get('file_type', 'unknown')
            type_count[node_type] = type_count.get(node_type, 0) + 1
        
        for node_type, count in type_count.items():
            info_text += f"  - {node_type}: {count}\n"
        
        self.graph_info.setText(info_text)
        
        # 绘制图谱
        self.graph_view.draw_graph(graph_data)

class DataVisualizationWidget(QWidget):
    """数据可视化控件"""
    def __init__(self, file_manager, graph_viewer):
        super().__init__()
        self.file_manager = file_manager
        self.graph_viewer = graph_viewer
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("数据统计与可视化")
        title_label.setFont(QFont('Times New Roman', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 图表容器
        charts_layout = QHBoxLayout()
        
        # 文件类型分布饼图
        type_chart = self._create_file_type_chart()
        type_chart_view = QChartView(type_chart)
        type_chart_view.setMinimumSize(400, 300)
        charts_layout.addWidget(type_chart_view)
        
        # 分类分布饼图
        category_chart = self._create_category_chart()
        category_chart_view = QChartView(category_chart)
        category_chart_view.setMinimumSize(400, 300)
        charts_layout.addWidget(category_chart_view)
        
        layout.addLayout(charts_layout)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        # 文件统计
        file_stats = QWidget()
        file_stats_layout = QVBoxLayout()
        file_stats_layout.addWidget(QLabel("文件统计"))
        
        total_files = len(self.file_manager.get_files())
        file_stats_layout.addWidget(QLabel(f"总文件数: {total_files}"))
        
        # 计算文件类型数量
        files = self.file_manager.get_files()
        type_count = {}
        for file in files:
            file_type = file.get('file_type', 'unknown')
            type_count[file_type] = type_count.get(file_type, 0) + 1
        
        for file_type, count in type_count.items():
            file_stats_layout.addWidget(QLabel(f"{file_type}: {count}"))
        
        file_stats.setLayout(file_stats_layout)
        stats_layout.addWidget(file_stats)
        
        # 图谱统计
        graph_stats = QWidget()
        graph_stats_layout = QVBoxLayout()
        graph_stats_layout.addWidget(QLabel("图谱统计"))
        
        try:
            stats = self.graph_viewer.get_graph_stats()
            graph_stats_layout.addWidget(QLabel(f"节点数量: {stats['node_count']}"))
            graph_stats_layout.addWidget(QLabel(f"边数量: {stats['edge_count']}"))
        except Exception as e:
            graph_stats_layout.addWidget(QLabel(f"获取统计信息失败: {str(e)}"))
        
        graph_stats.setLayout(graph_stats_layout)
        stats_layout.addWidget(graph_stats)
        
        layout.addLayout(stats_layout)
        
        # 刷新按钮
        refresh_button = QPushButton("刷新数据")
        refresh_button.clicked.connect(self.refresh_charts)
        layout.addWidget(refresh_button)
        
        self.setLayout(layout)
    
    def _create_file_type_chart(self):
        """创建文件类型分布饼图"""
        chart = QChart()
        chart.setTitle("文件类型分布")
        
        series = QPieSeries()
        
        # 获取文件类型数据
        files = self.file_manager.get_files()
        type_count = {}
        for file in files:
            file_type = file.get('file_type', 'unknown')
            type_count[file_type] = type_count.get(file_type, 0) + 1
        
        # 添加数据到系列
        for file_type, count in type_count.items():
            series.append(file_type, count)
        
        # 设置标签
        series.setLabelsVisible(True)
        
        chart.addSeries(series)
        return chart
    
    def _create_category_chart(self):
        """创建分类分布饼图"""
        chart = QChart()
        chart.setTitle("文件分类分布")
        
        series = QPieSeries()
        
        # 获取分类数据
        files = self.file_manager.get_files()
        category_count = {}
        for file in files:
            category = file.get('category', '未分类')
            category_count[category] = category_count.get(category, 0) + 1
        
        # 添加数据到系列
        for category, count in category_count.items():
            series.append(category, count)
        
        # 设置标签
        series.setLabelsVisible(True)
        
        chart.addSeries(series)
        return chart
    
    def refresh_charts(self):
        """刷新图表"""
        # 重新创建布局
        layout = self.layout()
        
        # 清除现有控件
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 重新添加控件
        # 标题
        title_label = QLabel("数据统计与可视化")
        title_label.setFont(QFont('Times New Roman', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 图表容器
        charts_layout = QHBoxLayout()
        
        # 文件类型分布饼图
        type_chart = self._create_file_type_chart()
        type_chart_view = QChartView(type_chart)
        type_chart_view.setMinimumSize(400, 300)
        charts_layout.addWidget(type_chart_view)
        
        # 分类分布饼图
        category_chart = self._create_category_chart()
        category_chart_view = QChartView(category_chart)
        category_chart_view.setMinimumSize(400, 300)
        charts_layout.addWidget(category_chart_view)
        
        layout.addLayout(charts_layout)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        # 文件统计
        file_stats = QWidget()
        file_stats_layout = QVBoxLayout()
        file_stats_layout.addWidget(QLabel("文件统计"))
        
        total_files = len(self.file_manager.get_files())
        file_stats_layout.addWidget(QLabel(f"总文件数: {total_files}"))
        
        # 计算文件类型数量
        files = self.file_manager.get_files()
        type_count = {}
        for file in files:
            file_type = file.get('file_type', 'unknown')
            type_count[file_type] = type_count.get(file_type, 0) + 1
        
        for file_type, count in type_count.items():
            file_stats_layout.addWidget(QLabel(f"{file_type}: {count}"))
        
        file_stats.setLayout(file_stats_layout)
        stats_layout.addWidget(file_stats)
        
        # 图谱统计
        graph_stats = QWidget()
        graph_stats_layout = QVBoxLayout()
        graph_stats_layout.addWidget(QLabel("图谱统计"))
        
        try:
            stats = self.graph_viewer.get_graph_stats()
            graph_stats_layout.addWidget(QLabel(f"节点数量: {stats['node_count']}"))
            graph_stats_layout.addWidget(QLabel(f"边数量: {stats['edge_count']}"))
        except Exception as e:
            graph_stats_layout.addWidget(QLabel(f"获取统计信息失败: {str(e)}"))
        
        graph_stats.setLayout(graph_stats_layout)
        stats_layout.addWidget(graph_stats)
        
        layout.addLayout(stats_layout)
        
        # 刷新按钮
        refresh_button = QPushButton("刷新数据")
        refresh_button.clicked.connect(self.refresh_charts)
        layout.addWidget(refresh_button)

class SettingsWidget(QWidget):
    """系统设置控件"""
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        layout = QVBoxLayout()
        
        # 存储设置
        storage_group = QWidget()
        storage_layout = QFormLayout()
        
        self.storage_dir_edit = QLineEdit(self.config_manager.get('storage.base_dir'))
        storage_layout.addRow("存储目录:", self.storage_dir_edit)
        
        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(self.browse_storage_dir)
        storage_layout.addRow("", browse_button)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # 搜索设置
        search_group = QWidget()
        search_layout = QFormLayout()
        
        self.max_results_edit = QLineEdit(str(self.config_manager.get('search.max_results')))
        search_layout.addRow("搜索结果限制:", self.max_results_edit)
        
        self.min_score_edit = QLineEdit(str(self.config_manager.get('search.min_score')))
        search_layout.addRow("搜索最小分数:", self.min_score_edit)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # 界面设置
        interface_group = QWidget()
        interface_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.config_manager.get('interface.theme'))
        interface_layout.addRow("主题:", self.theme_combo)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["list", "grid"])
        self.view_combo.setCurrentText(self.config_manager.get('interface.view'))
        interface_layout.addRow("视图:", self.view_combo)
        
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # 保存按钮
        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        # 重置按钮
        reset_button = QPushButton("重置为默认值")
        reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(reset_button)
        
        self.setLayout(layout)
    
    def browse_storage_dir(self):
        """浏览存储目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择存储目录", self.storage_dir_edit.text())
        if directory:
            self.storage_dir_edit.setText(directory)
    
    def save_settings(self):
        """保存设置"""
        # 存储设置
        self.config_manager.set('storage.base_dir', self.storage_dir_edit.text())
        
        # 搜索设置
        try:
            max_results = int(self.max_results_edit.text())
            self.config_manager.set('search.max_results', max_results)
        except ValueError:
            QMessageBox.warning(self, "警告", "搜索结果限制必须是整数")
            return
        
        try:
            min_score = float(self.min_score_edit.text())
            self.config_manager.set('search.min_score', min_score)
        except ValueError:
            QMessageBox.warning(self, "警告", "搜索最小分数必须是数字")
            return
        
        # 界面设置
        old_theme = self.config_manager.get('interface.theme')
        new_theme = self.theme_combo.currentText()
        self.config_manager.set('interface.theme', new_theme)
        self.config_manager.set('interface.view', self.view_combo.currentText())
        
        # 如果主题发生变化，提示用户重启应用
        if old_theme != new_theme:
            QMessageBox.information(self, "成功", "设置已保存。请重启应用以应用新主题。")
        else:
            QMessageBox.information(self, "成功", "设置已保存")
    
    def reset_settings(self):
        """重置为默认值"""
        reply = QMessageBox.question(self, "确认重置", "确定要将设置重置为默认值吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_default()
            
            # 刷新界面
            self.storage_dir_edit.setText(self.config_manager.get('storage.base_dir'))
            self.max_results_edit.setText(str(self.config_manager.get('search.max_results')))
            self.min_score_edit.setText(str(self.config_manager.get('search.min_score')))
            self.theme_combo.setCurrentText(self.config_manager.get('interface.theme'))
            self.view_combo.setCurrentText(self.config_manager.get('interface.view'))
            
            QMessageBox.information(self, "成功", "设置已重置为默认值")

class WorkflowManagementWidget(QWidget):
    """工作流管理控件"""
    def __init__(self, workflow_manager):
        super().__init__()
        self.workflow_manager = workflow_manager
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("工作流管理")
        title_label.setFont(QFont('Times New Roman', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 工作流列表
        self.workflow_list = QListWidget()
        self.workflow_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.workflow_list.customContextMenuRequested.connect(self.show_workflow_context_menu)
        self.workflow_list.itemClicked.connect(self.select_workflow)
        layout.addWidget(self.workflow_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_workflows)
        button_layout.addWidget(refresh_button)
        
        add_workflow_button = QPushButton("添加工作流")
        add_workflow_button.clicked.connect(self.add_workflow)
        button_layout.addWidget(add_workflow_button)
        
        execute_button = QPushButton("执行工作流")
        execute_button.clicked.connect(self.execute_workflow)
        button_layout.addWidget(execute_button)
        
        layout.addLayout(button_layout)
        
        # 工作流详情
        self.workflow_details = QWidget()
        details_layout = QVBoxLayout()
        
        self.name_label = QLabel("工作流名称:")
        details_layout.addWidget(self.name_label)
        
        self.type_label = QLabel("工作流类型:")
        details_layout.addWidget(self.type_label)
        
        self.enabled_label = QLabel("状态:")
        details_layout.addWidget(self.enabled_label)
        
        self.created_label = QLabel("创建时间:")
        details_layout.addWidget(self.created_label)
        
        # 日志列表
        log_label = QLabel("执行日志:")
        details_layout.addWidget(log_label)
        
        self.log_list = QListWidget()
        self.log_list.setMaximumHeight(200)
        details_layout.addWidget(self.log_list)
        
        self.workflow_details.setLayout(details_layout)
        layout.addWidget(self.workflow_details)
        
        self.setLayout(layout)
        self.refresh_workflows()
    
    def refresh_workflows(self):
        """刷新工作流列表"""
        workflows = self.workflow_manager.get_workflows()
        self.workflow_list.clear()
        for workflow in workflows:
            status = "启用" if workflow['enabled'] else "禁用"
            item = QListWidgetItem(f"{workflow['name']} ({workflow['type']}) - {status}")
            item.setData(Qt.ItemDataRole.UserRole, workflow)
            self.workflow_list.addItem(item)
    
    def select_workflow(self, item):
        """选择工作流"""
        workflow = item.data(Qt.ItemDataRole.UserRole)
        if not workflow:
            return
        
        # 显示工作流详情
        self.name_label.setText(f"工作流名称: {workflow['name']}")
        self.type_label.setText(f"工作流类型: {workflow['type']}")
        self.enabled_label.setText(f"状态: {'启用' if workflow['enabled'] else '禁用'}")
        self.created_label.setText(f"创建时间: {workflow['created_at']}")
        
        # 显示执行日志
        logs = self.workflow_manager.get_workflow_logs(workflow['id'])
        self.log_list.clear()
        for log in logs[:10]:  # 只显示最近10条日志
            log_text = f"[{log['executed_at']}] {log['status']}: {log['message']}"
            log_item = QListWidgetItem(log_text)
            self.log_list.addItem(log_item)
    
    def show_workflow_context_menu(self, pos):
        """显示工作流上下文菜单"""
        item = self.workflow_list.itemAt(pos)
        if not item:
            return
        
        workflow = item.data(Qt.ItemDataRole.UserRole)
        if not workflow:
            return
        
        menu = QMenu()
        
        toggle_action = QAction("禁用" if workflow['enabled'] else "启用", self)
        toggle_action.triggered.connect(lambda: self.toggle_workflow(workflow))
        menu.addAction(toggle_action)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self.edit_workflow(workflow))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_workflow(workflow))
        menu.addAction(delete_action)
        
        menu.exec(self.workflow_list.mapToGlobal(pos))
    
    def add_workflow(self):
        """添加工作流"""
        # 简单的工作流添加对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加工作流")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # 名称
        name_label = QLabel("工作流名称:")
        layout.addWidget(name_label)
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        # 类型
        type_label = QLabel("工作流类型:")
        layout.addWidget(type_label)
        type_combo = QComboBox()
        type_combo.addItems(["auto_classification", "tag_recommendation"])
        layout.addWidget(type_combo)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def on_ok():
            name = name_input.text().strip()
            workflow_type = type_combo.currentText()
            
            if not name:
                QMessageBox.warning(self, "警告", "请输入工作流名称")
                return
            
            # 创建默认配置
            if workflow_type == "auto_classification":
                config = {
                    'trigger': 'file_import',
                    'rules': [
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['关键词1', '关键词2'],
                            'category': '默认分类'
                        }
                    ]
                }
            else:  # tag_recommendation
                config = {
                    'trigger': 'file_import',
                    'rules': [
                        {
                            'condition': 'contains',
                            'field': 'content',
                            'value': ['关键词1', '关键词2'],
                            'tags': ['标签1', '标签2']
                        }
                    ]
                }
            
            result = self.workflow_manager.add_workflow(name, workflow_type, config)
            if result['success']:
                QMessageBox.information(self, "成功", "工作流添加成功")
                self.refresh_workflows()
                dialog.accept()
            else:
                QMessageBox.warning(self, "失败", result['message'])
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def edit_workflow(self, workflow):
        """编辑工作流"""
        # 简单的工作流编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑工作流")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # 名称
        name_label = QLabel("工作流名称:")
        layout.addWidget(name_label)
        name_input = QLineEdit(workflow['name'])
        layout.addWidget(name_input)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def on_ok():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "警告", "请输入工作流名称")
                return
            
            result = self.workflow_manager.update_workflow(workflow['id'], name, workflow['config'])
            if result['success']:
                QMessageBox.information(self, "成功", "工作流更新成功")
                self.refresh_workflows()
                dialog.accept()
            else:
                QMessageBox.warning(self, "失败", result['message'])
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def delete_workflow(self, workflow):
        """删除工作流"""
        reply = QMessageBox.question(self, "确认删除", f"确定要删除工作流 {workflow['name']} 吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.workflow_manager.delete_workflow(workflow['id'])
            if result['success']:
                QMessageBox.information(self, "成功", "工作流删除成功")
                self.refresh_workflows()
            else:
                QMessageBox.warning(self, "失败", result['message'])
    
    def toggle_workflow(self, workflow):
        """启用/禁用工作流"""
        new_status = not workflow['enabled']
        result = self.workflow_manager.toggle_workflow(workflow['id'], new_status)
        if result['success']:
            QMessageBox.information(self, "成功", f"工作流已{'启用' if new_status else '禁用'}")
            self.refresh_workflows()
        else:
            QMessageBox.warning(self, "失败", result['message'])
    
    def execute_workflow(self):
        """执行工作流"""
        selected_item = self.workflow_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "警告", "请选择要执行的工作流")
            return
        
        workflow = selected_item.data(Qt.ItemDataRole.UserRole)
        if not workflow:
            return
        
        # 执行工作流
        result = self.workflow_manager.execute_workflow(workflow['id'])
        if result['success']:
            QMessageBox.information(self, "成功", result['message'])
            # 刷新日志
            self.select_workflow(selected_item)
        else:
            QMessageBox.warning(self, "失败", result['message'])

class P2PFileSharingWidget(QWidget):
    """P2P文件共享控件"""
    def __init__(self, p2p_discovery, p2p_client, group_manager, file_manager, current_user):
        super().__init__()
        self.p2p_discovery = p2p_discovery
        self.p2p_client = p2p_client
        self.group_manager = group_manager
        self.file_manager = file_manager
        self.current_user = current_user
        
        # 设置背景样式
        self.setStyleSheet("""QWidget {
            background-color: #F8F9FA;
        }""")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("P2P文件共享")
        title_label.setFont(QFont('Times New Roman', 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""QTabWidget::pane {
            border: 1px solid #E0E0E0;
            background-color: #FFFFFF;
            border-radius: 8px;
        }
        QTabBar {
            background-color: #FFFFFF;
        }
        QTabBar::tab {
            padding: 10px 20px;
            font-size: 12px;
            color: #757575;
            border: none;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:hover {
            color: #2196F3;
        }
        QTabBar::tab:selected {
            color: #2196F3;
            border-bottom-color: #2196F3;
        }""")
        
        # 发现设备标签
        discover_tab = self._create_discover_tab()
        self.tab_widget.addTab(discover_tab, "发现设备")
        
        # 组管理标签
        groups_tab = self._create_groups_tab()
        self.tab_widget.addTab(groups_tab, "组管理")
        
        # 文件共享标签
        share_tab = self._create_share_tab()
        self.tab_widget.addTab(share_tab, "文件共享")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def _create_discover_tab(self):
        """创建发现设备标签"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 刷新按钮
        refresh_button = QPushButton("刷新设备列表")
        refresh_button.clicked.connect(self.refresh_devices)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(refresh_button)
        
        # 设备列表
        self.device_list = QListWidget()
        self.device_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 12px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background-color: #F0F2F5;
        }""")
        layout.addWidget(self.device_list)
        
        widget.setLayout(layout)
        return widget
    
    def _create_groups_tab(self):
        """创建组管理标签"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        create_group_button = QPushButton("创建组")
        create_group_button.clicked.connect(self.create_group)
        create_group_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(create_group_button)
        
        refresh_groups_button = QPushButton("刷新组列表")
        refresh_groups_button.clicked.connect(self.refresh_groups)
        refresh_groups_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #757575;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        button_layout.addWidget(refresh_groups_button)
        
        layout.addLayout(button_layout)
        
        # 组列表
        self.group_list = QListWidget()
        self.group_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 12px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background-color: #F0F2F5;
        }""")
        self.group_list.itemClicked.connect(self.select_group)
        layout.addWidget(self.group_list)
        
        # 组成员和文件
        self.group_details = QWidget()
        details_layout = QVBoxLayout()
        
        # 成员列表
        members_label = QLabel("成员:")
        details_layout.addWidget(members_label)
        
        self.members_list = QListWidget()
        self.members_list.setMaximumHeight(150)
        self.members_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px;
        }
        QListWidget::item {
            padding: 4px 8px;
        }""")
        details_layout.addWidget(self.members_list)
        
        # 文件列表
        files_label = QLabel("文件:")
        details_layout.addWidget(files_label)
        
        self.files_list = QListWidget()
        self.files_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px;
        }
        QListWidget::item {
            padding: 4px 8px;
        }""")
        details_layout.addWidget(self.files_list)
        
        self.group_details.setLayout(details_layout)
        layout.addWidget(self.group_details)
        
        widget.setLayout(layout)
        return widget
    
    def _create_share_tab(self):
        """创建文件共享标签"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 选择组
        group_layout = QHBoxLayout()
        group_label = QLabel("选择组:")
        group_layout.addWidget(group_label)
        
        self.group_combo = QComboBox()
        self.group_combo.setStyleSheet("""QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }
        QComboBox:focus {
            border-color: #2196F3;
        }""")
        group_layout.addWidget(self.group_combo)
        layout.addLayout(group_layout)
        
        # 上传文件按钮
        upload_button = QPushButton("上传文件")
        upload_button.clicked.connect(self.upload_file)
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(upload_button)
        
        # 共享文件列表
        self.shared_files_list = QListWidget()
        self.shared_files_list.setStyleSheet("""QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 12px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background-color: #F0F2F5;
        }""")
        layout.addWidget(self.shared_files_list)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_devices(self):
        """刷新设备列表"""
        devices = self.p2p_discovery.get_discovered_devices()
        self.device_list.clear()
        
        for device_id, device_info in devices.items():
            item = QListWidgetItem(f"{device_info['name']} ({device_info['ip']}:{device_info['port']})")
            item.setData(Qt.ItemDataRole.UserRole, device_info)
            self.device_list.addItem(item)
    
    def refresh_groups(self):
        """刷新组列表"""
        groups = self.group_manager.get_groups()
        self.group_list.clear()
        self.group_combo.clear()
        
        for group_id, group_info in groups.items():
            item = QListWidgetItem(f"{group_info['name']} (成员: {len(group_info['members'])})")
            item.setData(Qt.ItemDataRole.UserRole, group_info)
            self.group_list.addItem(item)
            self.group_combo.addItem(group_info['name'], group_id)
    
    def select_group(self, item):
        """选择组"""
        group_info = item.data(Qt.ItemDataRole.UserRole)
        if not group_info:
            return
        
        # 显示组成员
        self.members_list.clear()
        for member in group_info['members']:
            self.members_list.addItem(member)
        
        # 显示组文件
        self.files_list.clear()
        for file_info in group_info['files']:
            self.files_list.addItem(f"{file_info['filename']} (添加于: {file_info['added_at']})")
    
    def create_group(self):
        """创建组"""
        from PyQt6.QtWidgets import QInputDialog
        
        group_name, ok = QInputDialog.getText(self, "创建组", "请输入组名称:")
        if ok and group_name:
            result = self.group_manager.create_group(group_name, self.current_user['username'])
            if result['success']:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification("组创建成功", "success")
                self.refresh_groups()
            else:
                # 获取主窗口的Toast通知实例
                main_window = self.window()
                if hasattr(main_window, 'toast'):
                    main_window.toast.show_notification(f"组创建失败: {result['message']}", "error")
    
    def upload_file(self):
        """上传文件"""
        from PyQt6.QtWidgets import QFileDialog
        
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt);;PDF文件 (*.pdf);;图片文件 (*.jpg *.png)"
        )
        if not file_path:
            return
        
        # 选择组
        group_index = self.group_combo.currentIndex()
        if group_index == -1:
            # 获取主窗口的Toast通知实例
            main_window = self.window()
            if hasattr(main_window, 'toast'):
                main_window.toast.show_notification("请选择一个组", "warning")
            return
        
        group_id = self.group_combo.itemData(group_index)
        
        # 上传文件到组内所有成员
        groups = self.group_manager.get_groups()
        group_info = groups.get(group_id)
        if not group_info:
            return
        
        # 获取主窗口的Toast通知实例
        main_window = self.window()
        if hasattr(main_window, 'toast'):
            main_window.toast.show_notification("正在上传文件...", "info")
        
        # 上传文件到自己
        self.file_manager.save_shared_file(
            os.path.basename(file_path),
            open(file_path, 'rb').read(),
            group_id,
            self.current_user['username']
        )
        
        # 上传文件到其他成员
        devices = self.p2p_discovery.get_discovered_devices()
        for device_id, device_info in devices.items():
            result = self.p2p_client.upload_file(
                device_info['ip'],
                device_info['port'],
                file_path,
                group_id,
                self.current_user['username']
            )
            print(f"上传到 {device_info['name']}: {result}")
        
        # 添加文件到组
        self.group_manager.add_file_to_group(
            group_id,
            file_path,
            os.path.basename(file_path)
        )
        
        # 刷新组列表
        self.refresh_groups()
        
        # 显示成功通知
        if hasattr(main_window, 'toast'):
            main_window.toast.show_notification("文件上传成功", "success")

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("本地化智能文件管理系统")
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置窗口样式
        self.setStyleSheet("""QMainWindow {
            background-color: #FFFFFF;
        }""")
        
        # 连接窗口大小变化信号
        self.resizeEvent = self._on_resize
        
        # 初始化系统
        self.config_manager = ConfigManager()
        self.user_manager = UserManager(self.config_manager)
        
        # 登录
        self.current_user = None
        if not self._show_login_dialog():
            # 登录失败，退出应用
            sys.exit()
        
        # 添加快捷键
        self._setup_shortcuts()
        
        # 初始化其他系统组件
        index_dir = self.config_manager.get_index_dir()
        self.data_store = DataStore(index_dir)
        self.file_importer = FileImporter(self.config_manager, self.data_store)
        self.file_manager = FileManager(self.config_manager, self.data_store)
        self.search_engine = SearchEngine(self.config_manager, self.data_store)
        self.tag_manager = TagManager(self.config_manager, self.data_store)
        self.graph_viewer = GraphViewer(self.config_manager, self.data_store)
        self.workflow_manager = WorkflowManager(self.config_manager, self.data_store, self.file_manager, self.tag_manager)
        
        # 初始化P2P相关组件
        import uuid
        self.device_id = str(uuid.uuid4())
        self.device_name = f"{self.current_user['username']}'s Device"
        self.p2p_port = 5000
        
        self.group_manager = GroupManager(self.config_manager)
        self.p2p_discovery = P2PDiscovery(self.device_id, self.device_name, self.p2p_port)
        self.p2p_server = P2PServer('0.0.0.0', self.p2p_port, self.file_manager, self.group_manager)
        self.p2p_client = P2PClient()
        
        # 启动P2P服务
        self.p2p_discovery.start()
        self.p2p_server.start()
        
        # 初始化Toast通知
        self.toast = ToastNotification(self)
        
        # 初始化加载动画
        self.loading = LoadingWidget(self)
        
        # 初始化骨架屏
        self.skeleton = SkeletonWidget(self)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部导航栏
        self._setup_top_navigation()
        
        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""QTabWidget::pane {
            border: none;
            background-color: #F8F9FA;
        }
        QTabBar {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E0E0E0;
        }
        QTabBar::tab {
            padding: 12px 24px;
            font-size: 12px;
            color: #757575;
            border: none;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:hover {
            color: #2196F3;
        }
        QTabBar::tab:selected {
            color: #2196F3;
            border-bottom-color: #2196F3;
        }""")
        
        # 文件管理标签
        file_management_tab = FileManagementWidget(self.file_manager, self.file_importer)
        self.tab_widget.addTab(file_management_tab, "文件管理")
        
        # 搜索标签
        search_tab = SearchWidget(self.search_engine)
        self.tab_widget.addTab(search_tab, "智能搜索")
        
        # 标签管理标签
        tag_management_tab = TagManagementWidget(self.tag_manager, self.file_manager)
        self.tab_widget.addTab(tag_management_tab, "标签管理")
        
        # 知识图谱标签
        knowledge_graph_tab = KnowledgeGraphWidget(self.graph_viewer, self.file_manager)
        self.tab_widget.addTab(knowledge_graph_tab, "知识图谱")
        
        # 数据可视化标签
        data_visualization_tab = DataVisualizationWidget(self.file_manager, self.graph_viewer)
        self.tab_widget.addTab(data_visualization_tab, "数据可视化")
        
        # 工作流管理标签
        workflow_management_tab = WorkflowManagementWidget(self.workflow_manager)
        self.tab_widget.addTab(workflow_management_tab, "工作流管理")
        
        # 用户管理标签（仅管理员可见）
        if self.current_user['role'] == 'admin':
            user_management_tab = UserManagementWidget(self.user_manager)
            self.tab_widget.addTab(user_management_tab, "用户管理")
        
        # P2P文件共享标签
        p2p_tab = P2PFileSharingWidget(self.p2p_discovery, self.p2p_client, self.group_manager, self.file_manager, self.current_user)
        self.tab_widget.addTab(p2p_tab, "P2P文件共享")
        
        # 设置标签
        settings_tab = SettingsWidget(self.config_manager)
        self.tab_widget.addTab(settings_tab, "系统设置")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""QStatusBar {
            background-color: #F8F9FA;
            color: #757575;
            font-size: 10px;
            font-family: '微软雅黑', 'Times New Roman';
            border-top: 1px solid #E0E0E0;
        }""")
        self.status_bar.showMessage(f"就绪 - 当前用户: {self.current_user['username']} (角色: {self.current_user['role']})")
    
    def _on_resize(self, event):
        """窗口大小变化事件处理"""
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 获取当前窗口大小
        width = self.width()
        
        # 根据窗口宽度调整各个组件的布局
        # 这里可以根据实际需求进行调整
        # 例如，当窗口宽度小于某个阈值时，调整标签页的布局
        
        # 调整Toast通知的位置
        if hasattr(self, 'toast'):
            self.toast.adjustSize()
            x = self.width() - self.toast.width() - 20
            y = 60  # 避开顶部导航栏
            self.toast.setGeometry(x, y, self.toast.width(), self.toast.height())
        
        # 调整加载动画的位置
        if hasattr(self, 'loading'):
            self.loading.adjustSize()
            x = self.width() // 2 - self.loading.width() // 2
            y = self.height() // 2 - self.loading.height() // 2
            self.loading.setGeometry(x, y, self.loading.width(), self.loading.height())
    
    def _setup_top_navigation(self):
        """设置顶部导航栏"""
        # 创建顶部工具栏
        toolbar = QToolBar()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet("""QToolBar {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E0E0E0;
            spacing: 20px;
        }""")
        self.addToolBar(toolbar)
        
        # 左侧Logo
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 0, 20, 0)
        
        logo_label = QLabel()
        logo_label.setFixedSize(32, 32)
        # 创建Logo
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#2196F3"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "L")
        painter.end()
        logo_label.setPixmap(pixmap)
        
        # 添加Logo动画效果
        logo_label.setStyleSheet("""QLabel:hover {
            /* 动画效果通过代码实现 */
        }""")
        
        logo_layout.addWidget(logo_label)
        toolbar.addWidget(logo_widget)
        
        # 中央搜索框
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件...")
        self.search_input.setFixedHeight(32)
        self.search_input.setFixedWidth(400)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #F5F5F5;
                border: none;
                border-radius: 16px;
                padding: 0 16px;
                font-size: 12px;
            }
            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 1px solid #2196F3;
                outline: none;
            }
        """)
        
        # 搜索按钮
        search_button = QPushButton()
        search_button.setFixedSize(32, 32)
        search_button.setStyleSheet("""QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 16px;
            margin-left: 8px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }""")
        search_button.setText("🔍")
        search_button.clicked.connect(self._focus_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        toolbar.addWidget(search_widget)
        
        # 右侧用户头像
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(20, 0, 20, 0)
        
        self.user_avatar = QLabel()
        self.user_avatar.setFixedSize(40, 40)
        # 创建用户头像
        avatar_pixmap = QPixmap(40, 40)
        avatar_pixmap.fill(QColor("#9E9E9E"))
        painter = QPainter(avatar_pixmap)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        initial = self.current_user['username'][0].upper()
        painter.drawText(avatar_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initial)
        painter.end()
        self.user_avatar.setPixmap(avatar_pixmap)
        self.user_avatar.setStyleSheet("""
            QLabel {
                border-radius: 20px;
            }
        """)
        
        # 添加用户菜单
        self.user_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_avatar.mousePressEvent = self._show_user_menu
        
        user_layout.addWidget(self.user_avatar)
        toolbar.addWidget(user_widget)
    
    def _show_user_menu(self, event):
        """显示用户菜单"""
        menu = QMenu(self)
        
        profile_action = QAction("个人资料", self)
        menu.addAction(profile_action)
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self._logout)
        menu.addAction(logout_action)
        
        # 显示菜单
        menu.exec(self.user_avatar.mapToGlobal(event.pos()))
    
    def _open_settings(self):
        """打开设置标签"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "系统设置":
                self.tab_widget.setCurrentIndex(i)
                break
    
    def _logout(self):
        """退出登录"""
        reply = QMessageBox.question(self, "确认退出", "确定要退出登录吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # 重新显示登录对话框
            self.current_user = None
            if not self._show_login_dialog():
                # 登录失败，退出应用
                sys.exit()
            else:
                # 登录成功，更新状态栏
                self.status_bar.showMessage(f"就绪 - 当前用户: {self.current_user['username']} (角色: {self.current_user['role']})")
                # 更新用户头像
                avatar_pixmap = QPixmap(40, 40)
                avatar_pixmap.fill(QColor("#9E9E9E"))
                painter = QPainter(avatar_pixmap)
                painter.setPen(QColor("#FFFFFF"))
                painter.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
                initial = self.current_user['username'][0].upper()
                painter.drawText(avatar_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initial)
                painter.end()
                self.user_avatar.setPixmap(avatar_pixmap)
    
    def _show_login_dialog(self):
        """显示登录对话框"""
        dialog = LoginDialog(self.user_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_user = dialog.login_result
            return True
        return False
    
    def _setup_shortcuts(self):
        """设置快捷键"""
        # 创建动作
        import_action = QAction("导入文件", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_file)
        
        search_action = QAction("搜索", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self._focus_search)
        
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_current_tab)
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # 添加到主窗口
        self.addAction(import_action)
        self.addAction(search_action)
        self.addAction(refresh_action)
        self.addAction(exit_action)
    
    def _import_file(self):
        """导入文件快捷键处理"""
        # 获取当前标签页
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'import_file'):
            current_widget.import_file()
    
    def _focus_search(self):
        """聚焦搜索框快捷键处理"""
        # 切换到搜索标签页
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "智能搜索":
                self.tab_widget.setCurrentIndex(i)
                # 聚焦搜索输入框
                current_widget = self.tab_widget.currentWidget()
                if hasattr(current_widget, 'search_input'):
                    current_widget.search_input.setFocus()
                break
    
    def _refresh_current_tab(self):
        """刷新当前标签页快捷键处理"""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'refresh_files'):
            current_widget.refresh_files()
        elif hasattr(current_widget, 'refresh_charts'):
            current_widget.refresh_charts()
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(self, "确认退出", "确定要退出系统吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

def set_app_style(app, theme='light'):
    """设置应用样式
    
    Args:
        app: QApplication实例
        theme: 主题名称 ('light' 或 'dark')
    """
    # 设置基本样式
    app.setStyle("Fusion")
    
    if theme == 'dark':
        # 深色主题
        app.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QTabWidget::pane {
                background-color: #3d3d3d;
                border: 1px solid #5d5d5d;
            }
            QTabBar::tab {
                background-color: #4d4d4d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #5d5d5d;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                border-bottom: 2px solid #4A90E2;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2A6090;
            }
            QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #5d5d5d;
                padding: 4px;
                border-radius: 4px;
            }
            QListWidget {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #5d5d5d;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #4d4d4d;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QComboBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #5d5d5d;
                padding: 4px;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
            }
            QToolBar {
                background-color: #3d3d3d;
                border: none;
            }
            QStatusBar {
                background-color: #3d3d3d;
                color: #ffffff;
            }
        """)
    else:
        # 浅色主题
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTabWidget::pane {
                background-color: #ffffff;
                border: 1px solid #dddddd;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 16px;
                border: 1px solid #dddddd;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #4A90E2;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2A6090;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 4px;
                border-radius: 4px;
            }
            QListWidget {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                padding: 4px;
                border-radius: 4px;
            }
            QLabel {
                color: #333333;
            }
            QToolBar {
                background-color: #e0e0e0;
                border: none;
            }
            QStatusBar {
                background-color: #e0e0e0;
                color: #333333;
            }
        """)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式为浅色主题
    set_app_style(app, 'light')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

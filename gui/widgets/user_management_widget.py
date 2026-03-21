#!/usr/bin/env python3
"""
用户管理控件模块
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMenu, QDialog, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        
        edit_role_action = menu.addAction("修改角色")
        edit_role_action.triggered.connect(lambda: self.edit_user_role(user))
        
        change_password_action = menu.addAction("修改密码")
        change_password_action.triggered.connect(lambda: self.change_user_password(user))
        
        delete_action = menu.addAction("删除用户")
        delete_action.triggered.connect(lambda: self.delete_user(user))
        
        menu.exec(self.user_list.mapToGlobal(pos))
    
    def add_user(self):
        """添加用户"""
        from gui.dialogs.register_dialog import RegisterDialog
        dialog = RegisterDialog(self.user_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_users()
    
    def edit_user_role(self, user):
        """修改用户角色"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QMessageBox
        
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
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
        
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
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除用户 {user['username']} 吗？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.user_manager.delete_user(user['id'])
            if result['success']:
                QMessageBox.information(self, "成功", "用户删除成功")
                self.refresh_users()
            else:
                QMessageBox.warning(self, "失败", result['message'])

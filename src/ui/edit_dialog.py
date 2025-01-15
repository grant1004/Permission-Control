from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QListWidget, QPushButton, QLineEdit, QListWidgetItem
)
from PyQt6.QtCore import Qt


class EditPermissionDialog(QDialog):
    def __init__(self, permission_name, default_value, current_roles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Permission")
        self.setModal(True)
        self.setMinimumWidth(400)

        # 存儲當前值
        self.permission_name = permission_name
        self.current_roles = current_roles

        # 預定義的角色列表
        self.available_roles = [
            "AM", "Battery", "CSD_PR", "CSD_T", "Charger",
            "Derailleur", "Engineering", "FAE", "FW", "HW",
            "ME", "Motor", "PM", "Production_Line", "Q",
            "SW", "Sales"
        ]

        self.setup_ui(permission_name, default_value, current_roles)

    def setup_ui(self, permission_name, default_value, current_roles):
        layout = QVBoxLayout(self)

        # Permission Name (唯讀)
        name_layout = QHBoxLayout()
        name_label = QLabel("Permission Name:")
        name_value = QLabel(permission_name)
        name_value.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_value)
        layout.addLayout(name_layout)

        # Default Value (下拉選單)
        default_layout = QHBoxLayout()
        default_label = QLabel("Default Value:")
        self.default_combo = QComboBox()
        self.default_combo.addItems(["True", "False"])
        self.default_combo.setCurrentText(str(default_value))
        self.default_combo.setStyleSheet( "color : white; ")
        default_layout.addWidget(default_label)
        default_layout.addWidget(self.default_combo)
        layout.addLayout(default_layout)

        # Roles 管理區域
        roles_label = QLabel("Roles:")
        layout.addWidget(roles_label)

        # 角色管理區域的水平布局
        roles_layout = QHBoxLayout()

        # 已選擇的角色列表
        self.selected_roles_list = QListWidget()
        self.selected_roles_list.addItems(current_roles)

        # 可用角色列表
        self.available_roles_list = QListWidget()
        available_roles = [role for role in self.available_roles if role not in current_roles]
        self.available_roles_list.addItems(available_roles)

        # 按鈕區域
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("→")
        self.remove_button = QPushButton("←")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        # 連接按鈕信號
        self.add_button.clicked.connect(self.add_role)
        self.remove_button.clicked.connect(self.remove_role)

        # 添加所有元素到角色布局
        roles_layout.addWidget(self.available_roles_list)
        roles_layout.addLayout(button_layout)
        roles_layout.addWidget(self.selected_roles_list)

        layout.addLayout(roles_layout)

        # 確認和取消按鈕
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout.addLayout(buttons_layout)

    def add_role(self):
        current_item = self.available_roles_list.currentItem()
        if current_item:
            # 創建新的 QListWidgetItem
            new_item = QListWidgetItem( "* " + current_item.text())
            self.selected_roles_list.addItem(new_item)
            self.available_roles_list.takeItem(self.available_roles_list.row(current_item))

    def remove_role(self):
        current_item = self.selected_roles_list.currentItem()
        if current_item:
            self.available_roles_list.addItem(current_item.text())
            self.selected_roles_list.takeItem(self.selected_roles_list.row(current_item))

    def get_values(self):
        selected_roles = []
        for i in range(self.selected_roles_list.count()):
            selected_roles.append(self.selected_roles_list.item(i).text())

        return {
            'default_value': self.default_combo.currentText() == "True",
            'roles': selected_roles
        }
import sys
import os
import json
import boto3
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt
from .edit_dialog import EditPermissionDialog
from ..models.aws_config import AWSConfig
from .circle_progress_dialog import CircleProgressDialog
from .circle_progress_dialog import UploadProgressCallback


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Permission Control System")
        self.setGeometry(100, 100, 1000, 600)
        self.setup_ui()

        # AWS 設定
        self.aws_config = AWSConfig()
        self.session = boto3.Session(**self.aws_config.credentials)
        self.s3_client = self.session.client('s3')

        # download permissions.json
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.local_json_path = os.path.join(self.base_dir, '..', 'models', 'json', 'permissions.json')
        self.load_permissions()

    def setup_ui(self):
        # 創建中央視窗
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 創建主要佈局
        main_layout = QVBoxLayout(central_widget)

        # 搜尋列佈局
        search_layout = QHBoxLayout()
        self.search_input_permission = QLineEdit()
        self.search_input_permission.setPlaceholderText("Search Permission...")
        self.search_input_permission.setStyleSheet( "color: white;" )
        self.search_input_permission.textChanged.connect(self.filter_permissions)
        search_layout.addWidget(self.search_input_permission)

        self.search_input_roles = QLineEdit()
        self.search_input_roles.setPlaceholderText("Search Roles...")
        self.search_input_roles.setStyleSheet("color: white;")
        self.search_input_roles.textChanged.connect(self.filter_roles)

        search_layout.addWidget(self.search_input_roles)

        # 添加搜尋佈局到主佈局
        main_layout.addLayout(search_layout)

        # 創建表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Permission Name", "Default", "Roles"])

        # 設置表格列寬
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.table)

        # 按鈕佈局
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit")
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.setEnabled(False)  # 初始時禁用保存按鈕
        self.cancel_button.setEnabled(False)  # 初始時禁用保存按鈕

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        # 連接按鈕信號
        self.edit_button.clicked.connect(self.enable_editing)
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(self.cancel_changes)

        main_layout.addLayout(button_layout)

    def load_permissions(self):
        try:
            # 顯示進度對話框
            progress_dialog = CircleProgressDialog(self)
            progress_dialog.show()

            # 確保目標資料夾存在
            os.makedirs(os.path.dirname(self.local_json_path), exist_ok=True)

            # 從 S3 下載檔案
            progress_callback = UploadProgressCallback(progress_dialog)
            try:
                self.s3_client.download_file(
                    self.aws_config.bucket,
                    'InHouseTool/permissions.json',
                    self.local_json_path,
                    Callback=progress_callback
                )
            except Exception as e:
                progress_dialog.close()
                raise Exception(f"Failed to download from S3: {str(e)}")

            # 讀取下載的 JSON 檔案
            try:
                with open(self.local_json_path, 'r', encoding='utf-8') as file:
                    permissions = json.load(file)
                    self.populate_table(permissions)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON format: {str(e)}")

            progress_dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Error loading permissions: {str(e)}")

    def populate_table(self, permissions):
        self.table.setRowCount(len(permissions['Permissions']))
        for row, (key, value) in enumerate(permissions['Permissions'].items()):
            # print( row )
            # Permission Name
            name_item = QTableWidgetItem(key)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            # Default Value
            default_item = QTableWidgetItem(str(value.get('DefaultValue', False)))
            default_item.setFlags(default_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, default_item)

            # Roles
            roles = ', '.join(value.get('AllowedRoles', []))
            roles_item = QTableWidgetItem(roles)
            roles_item.setFlags(roles_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, roles_item)

    def filter_permissions(self, text):
        for row in range(self.table.rowCount()):
            show = False
            col = 0  # permission
            item = self.table.item(row, col)
            if item and text.lower() in item.text().lower():
                show = True
            self.table.setRowHidden(row, not show)

    def filter_roles(self, text):
        for row in range(self.table.rowCount()):
            show = False
            col = 2  # role
            item = self.table.item(row, col)
            if item and text.lower() in item.text().lower():
                show = True
            self.table.setRowHidden(row, not show)

    def enable_editing(self):
        # 獲取當前選中的行
        current_row = self.table.currentRow()
        if current_row < 0:
            return  # 如果沒有選中行，則返回

        # 獲取當前行的數據
        permission_name = self.table.item(current_row, 0).text()
        default_value = self.table.item(current_row, 1).text()
        roles = self.table.item(current_row, 2).text().split(', ')

        # 創建並顯示編輯對話框
        dialog = EditPermissionDialog(
            permission_name=permission_name,
            default_value=default_value,
            current_roles=roles,
            parent=self
        )

        # 如果用戶點擊確定
        if dialog.exec() == EditPermissionDialog.DialogCode.Accepted:
            # 獲取修改後的值
            new_values = dialog.get_values()

            new_roles = [r.replace("* ", "") for r in new_values['roles']]
            # 更新表格
            self.table.item(current_row, 1).setText(str(new_values['default_value']))
            self.table.item(current_row, 2).setText(', '.join(new_roles))

            # 啟用保存按鈕
            self.save_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

    def save_changes(self):
        try:
            # 創建進度對話框
            progress_dialog = CircleProgressDialog(self)
            progress_dialog.show()

            # 設定 AWS
            aws_config = AWSConfig()
            session = boto3.Session(**aws_config.credentials)
            s3_client = session.client('s3')

            # 獲取當前腳本的絕對路徑
            base_dir = os.path.dirname(os.path.abspath(__file__))

            # 構建本地 permission.json 的完整路徑
            local_json_path = os.path.join(base_dir, '..', 'models', 'json', 'permissions.json')

            # 讀取原始 JSON 文件
            with open(local_json_path, 'r', encoding='utf-8') as file:
                permissions = json.load(file)

            progress_callback = UploadProgressCallback(progress_dialog)
            s3_client.upload_file(
                local_json_path,
                aws_config.bucket,
                'InHouseTool/backup/permissions.json',
                Callback=progress_callback
            )

            # 更新 permissions
            for row in range(self.table.rowCount()):
                permission_name = self.table.item(row, 0).text()
                default_value = self.table.item(row, 1).text() == 'True'
                roles = self.table.item(row, 2).text().split(', ') if self.table.item(row, 2).text() else []
                roles = [ r.replace("* ", "") for r in roles ]
                # 更新對應的權限
                permissions['Permissions'][permission_name] = {
                    'AllowedRoles': roles,
                    'DefaultValue': default_value

                }

            # 先本地保存
            with open(local_json_path, 'w', encoding='utf-8') as file:
                json.dump(permissions, file, indent=4, ensure_ascii=False)

            progress_callback = UploadProgressCallback(progress_dialog)
            s3_client.upload_file(
                local_json_path,
                aws_config.bucket,
                'InHouseTool/permissions.json',
                Callback=progress_callback
            )

            # 顯示成功消息
            progress_dialog.close()
            QMessageBox.information(self, "Save Successful", "Permissions updated locally and uploaded to AWS S3.")

            self.edit_button.setEnabled(True)
            self.save_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving: {str(e)}")

    def cancel_changes(self):
        # 讀取下載的 JSON 檔案
        try:
            self.table.clear()
            with open(self.local_json_path, 'r', encoding='utf-8') as file:
                permissions = json.load(file)
                self.populate_table(permissions)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {str(e)}")

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

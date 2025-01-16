import sys
import os
import json
import boto3
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import (Qt, QThread, pyqtSignal)
from .edit_dialog import EditPermissionDialog
from ..models.aws_config import AWSConfig
from .blur_progress_dialog import creat_progress_dialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Permission Control System")
        self.setGeometry(100, 100, 1000, 600)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags( self.windowFlags() | Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint )
        self.setup_ui()

        # AWS 設定
        self.aws_config = AWSConfig()
        self.session = boto3.Session(**self.aws_config.credentials)
        self.s3_client = self.session.client('s3')

        # Progress View
        self.progress_dialog = None
        self.uploading_progress_dialog = creat_progress_dialog(self, "Uploading to S3 ...")
        self.load_progress_dialog = creat_progress_dialog(self, "Loading permissions.json from S3 ...")


        # download permissions.json
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.local_json_path = os.path.join(self.base_dir, '..', 'models', 'json', 'permissions.json')
        self.load_permissions_worker = LoadWorker(self)
        self.load_permissions_worker.finished.connect(self.on_load_complete)
        self.load_permissions_worker.error.connect(self.on_load_error)

        #save
        self.save_worker = SaveWorker(self)
        self.save_worker.finished.connect(self.on_save_complete)
        self.save_worker.error.connect(self.on_save_error)


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

    # region Load permission Worker : doing, finished, error
    def load_permissions(self):
        self.show_progress(self.load_progress_dialog)
        self.load_permissions_worker.start()
        print( "Load permissions worker started" )

    def on_load_complete(self):
        self.hide_progress(self.load_progress_dialog)
        # 讀取下載的 JSON 檔案
        print( "Complete load permissions json")
        try:
            with open(self.local_json_path, 'r', encoding='utf-8') as file:
                permissions = json.load(file)
                self.populate_table(permissions)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Load Error",
                                 f"An error occurred while Loading: Invalid JSON format: {str(e)}")

    def on_load_error(self, error_message):
        self.hide_progress(self.load_progress_dialog)
        QMessageBox.critical(self, "Load Error",
                             f"An error occurred while Loading: {error_message}")
    #========================================================================#




    # region Save Worker : doing, finished, error
    def save_changes(self):
        self.show_progress(self.uploading_progress_dialog)
        self.save_worker.start()

    def on_save_complete(self):
        self.hide_progress(self.uploading_progress_dialog)
        QMessageBox.information(self, "Save Successful",
                                "Permissions updated locally and uploaded to AWS S3.")
        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def on_save_error(self, error_message):
        self.hide_progress(self.uploading_progress_dialog)
        QMessageBox.critical(self, "Save Error",
                             f"An error occurred while saving: {error_message}")
    #========================================================================#


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



    def cancel_changes(self):
        # 讀取下載的 JSON 檔案
        try:
            self.table.clear()
            with open(self.local_json_path, 'r', encoding='utf-8') as file:
                permissions = json.load(file)
                self.populate_table(permissions)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {str(e)}")

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(False)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 通知子視窗重新調整大小
        if self.progress_dialog:
            self.progress_dialog.resize(self.size())  # 同步更新子視窗大小
            self.progress_dialog.blur_container.resize(self.size())
            print(f"Parent resized: {self.size()}")

    # 显示对话框时
    def show_progress(self, dialog):
        if dialog:
            dialog.show()
            self.progress_dialog = dialog  # 更新当前活动的对话框引用

    # 隐藏对话框时
    def hide_progress(self, dialog):
        if dialog:
            dialog.hide()
            if self.progress_dialog == dialog:
                self.progress_dialog = None


class SaveWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        try:
            # 讀取原始 JSON 文件
            with open(self.main_window.local_json_path, 'r', encoding='utf-8') as file:
                permissions = json.load(file)

            self.main_window.s3_client.upload_file(
                self.main_window.local_json_path,
                self.main_window.aws_config.bucket,
                'InHouseTool/backup/permissions.json'
            )

            # 更新 permissions
            for row in range(self.main_window.table.rowCount()):
                permission_name = self.main_window.table.item(row, 0).text()
                default_value = self.main_window.table.item(row, 1).text() == 'True'
                roles = self.main_window.table.item(row, 2).text().split(', ') if self.main_window.table.item(row, 2).text() else []
                roles = [r.replace("* ", "") for r in roles]
                permissions['Permissions'][permission_name] = {
                    'AllowedRoles': roles,
                    'DefaultValue': default_value
                }

            # 本地保存
            with open(self.main_window.local_json_path, 'w', encoding='utf-8') as file:
                json.dump(permissions, file, indent=4, ensure_ascii=False)

            self.main_window.s3_client.upload_file(
                self.main_window.local_json_path,
                self.main_window.aws_config.bucket,
                'InHouseTool/permissions.json'
            )

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class LoadWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        try:
            # 確保目標資料夾存在
            os.makedirs(os.path.dirname(self.main_window.local_json_path), exist_ok=True)

            # 從 S3 下載檔案
            try:
                self.main_window.s3_client.download_file(
                    self.main_window.aws_config.bucket,
                    'InHouseTool/permissions.json',
                    self.main_window.local_json_path )
                print( f"Save Permission done {self.main_window.local_json_path}")
            except Exception as e:
                raise Exception(f"Failed to download from S3: {str(e)}")

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
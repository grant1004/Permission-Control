from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                             QWidget, QProgressBar)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor


class BlurProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.hide()

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # 設置間距為 0

        # 霧化背景容器
        self.blur_container = QWidget(self)
        self.blur_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 160);
            }
        """)

        # 進度條容器
        self.progress_container = QWidget()
        self.progress_container.setFixedSize(300, 150)
        self.progress_container.setStyleSheet("""
            QWidget {
                border-radius: 10px;
            }
        """)

        # 進度條容器的布局
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 標籤
        self.title = "Uploading..."
        self.label = QLabel(self.title)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(250, 6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
        """)

        progress_layout.addWidget(self.label)
        progress_layout.addWidget(self.progress_bar)

        container_layout = QVBoxLayout(self.blur_container)
        container_layout.addWidget(self.progress_container, 0,Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.blur_container)

    def showEvent(self, event):
        super().showEvent(event)

        if self.parent():
            # 獲取父視窗的位置和大小
            parent_geo = self.parent().geometry()

            self.setGeometry(0,0, parent_geo.width(), parent_geo.height())
            # 設置對話框大小為父視窗的客戶區域大小
            self.resize(self.parent().size())

            # 調整霧化背景大小
            self.blur_container.resize(self.size())

    def SetTitle(self, title):
        self.title = title
        self.label.setText(self.title)



def creat_progress_dialog(parent_window, title = "Uploading..."):
    dialog = BlurProgressDialog(parent_window)
    dialog.SetTitle(title)
    dialog.hide()
    return dialog
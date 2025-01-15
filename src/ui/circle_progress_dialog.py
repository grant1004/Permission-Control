from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRectF


class UploadProgressCallback:
    def __init__(self, progress_dialog):
        self._progress_dialog = progress_dialog
        self._total_bytes = 0
        self._uploaded_bytes = 0

    def __call__(self, bytes_amount):
        if self._total_bytes == 0:
            self._total_bytes = bytes_amount
        else:
            self._uploaded_bytes += bytes_amount
            progress = min(self._uploaded_bytes / self._total_bytes, 1.0)
            self._progress_dialog.progress = progress


class CircleProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        self.setFixedSize(200, 200)
        self._progress = 0

        layout = QVBoxLayout()
        self.label = QLabel("Uploading...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.label)
        self.setLayout(layout)

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        percentage = int(value * 100)
        self.label.setText(f"Uploading... {percentage}%")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 繪製半透明背景
        painter.setBrush(QColor(0, 0, 0, 127))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # 繪製進度圓
        pen = QPen()
        pen.setWidth(10)
        painter.setPen(pen)

        rect = QRectF(50, 50, 100, 100)

        # 背景圓
        pen.setColor(QColor(200, 200, 200))
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # 進度圓
        pen.setColor(QColor(0, 150, 255))
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -self.progress * 360 * 16)
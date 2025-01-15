import sys
import shutil
import os
import atexit



def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


def cleanup_temp():
    try:
        # 獲取 TEMP 目錄
        temp = os.getenv('TEMP', os.getenv('TMP', ''))
        if temp:
            # 尋找所有 _MEI 開頭的目錄
            for item in os.listdir(temp):
                item_path = os.path.join(temp, item)
                if item.startswith('_MEI') and os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path, ignore_errors=True)
                    except:
                        pass
    except:
        pass



# 你的主程式代碼...
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from qt_material import apply_stylesheet
    from src.ui import MainWindow
    # 註冊程式退出時的清理函數
    atexit.register(cleanup_temp)
    main()
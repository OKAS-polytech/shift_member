"""
PyQt6 GUIアプリケーションのエントリーポイント。
"""
import sys
from PyQt6.QtWidgets import QApplication

from shift_management.manager import ShiftManager
from shift_management_gui.main_window import MainWindow
from shift_management_gui.controller import ShiftController

def main():
    """
    アプリケーションを初期化し、実行する。
    """
    # 1. PyQtアプリケーションインスタンスを作成
    app = QApplication(sys.argv)

    # 2. MVCコンポーネントをインスタンス化
    # Model: ビジネスロジックとデータ管理
    shift_manager = ShiftManager(data_dir="data")

    # View: UIの表示
    main_view = MainWindow()

    # Controller: ModelとViewの連携
    # (コントローラがViewにModelを接続し、イベントを処理する)
    controller = ShiftController(manager=shift_manager, view=main_view)

    # 3. メインウィンドウを表示
    main_view.show()

    # 4. アプリケーションのイベントループを開始
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

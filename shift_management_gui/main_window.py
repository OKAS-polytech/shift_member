"""
GUIアプリケーションのメインウィンドウ（View）を定義するモジュール。
"""
import datetime
import calendar
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QHeaderView, QMenuBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウ。
    カレンダー表示、ナビゲーション、メニューを提供する。
    """
    # --- Signals ---
    # シグナルはコントローラにアクションを通知するために使用される

    # 月の変更が要求されたときに発行される (e.g., "前月", "次月" ボタン)
    month_change_requested = pyqtSignal(int)  # direction: -1 for prev, 1 for next

    # 社員管理ダイアログの表示が要求されたときに発行される
    manage_employees_requested = pyqtSignal()

    # シフトの割り当てが要求されたときに発行される (日付、シフトタイプ)
    assign_shift_requested = pyqtSignal(datetime.date, str)

    # アプリケーション終了が要求されたときに発行される
    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        """
        MainWindowを初期化する。
        """
        super().__init__(parent)
        self.setWindowTitle("シフト管理アプリケーション")
        self.setGeometry(100, 100, 800, 600)

        # --- UIのセットアップ ---
        self._setup_ui()

    def _setup_ui(self):
        """
        UIコンポーネントを初期化し、レイアウトを設定する。
        """
        # メニューバー
        self._create_menu_bar()

        # メインウィジェットとレイアウト
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 月ナビゲーション
        nav_layout = QHBoxLayout()
        self.prev_month_button = QPushButton("前月")
        self.next_month_button = QPushButton("次月")
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.prev_month_button)
        nav_layout.addWidget(self.month_label)
        nav_layout.addWidget(self.next_month_button)
        main_layout.addLayout(nav_layout)

        # シフトカレンダーテーブル
        self.calendar_table = QTableWidget()
        self.calendar_table.setColumnCount(3)
        self.calendar_table.setHorizontalHeaderLabels(["日付", "早番", "遅番"])
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.calendar_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_layout.addWidget(self.calendar_table)

        # --- シグナルとスロットの接続 ---
        self.prev_month_button.clicked.connect(lambda: self.month_change_requested.emit(-1))
        self.next_month_button.clicked.connect(lambda: self.month_change_requested.emit(1))
        self.calendar_table.customContextMenuRequested.connect(self._show_calendar_context_menu)

    def _create_menu_bar(self):
        """
        メニューバーを作成する。
        """
        menu_bar = self.menuBar()

        # ファイルメニュー
        file_menu = menu_bar.addMenu("ファイル")
        exit_action = file_menu.addAction("終了")
        exit_action.triggered.connect(self.exit_requested.emit)

        # 社員メニュー
        employee_menu = menu_bar.addMenu("社員")
        manage_employees_action = employee_menu.addAction("社員を管理")
        manage_employees_action.triggered.connect(self.manage_employees_requested.emit)

    def _show_calendar_context_menu(self, pos):
        """
        カレンダーテーブルの右クリック時にコンテキストメニューを表示する。
        """
        selected_item = self.calendar_table.itemAt(pos)
        if not selected_item:
            return

        row = selected_item.row()
        date_str = self.calendar_table.item(row, 0).text().split(' ')[0]
        year = self.current_date.year
        month = self.current_date.month
        day = int(date_str)
        target_date = datetime.date(year, month, day)

        menu = QMenuBar()
        assign_early_action = menu.addAction("早番を割り当てる")
        assign_late_action = menu.addAction("遅番を割り当てる")

        action = menu.exec(self.calendar_table.mapToGlobal(pos))

        if action == assign_early_action:
            self.assign_shift_requested.emit(target_date, "early")
        elif action == assign_late_action:
            self.assign_shift_requested.emit(target_date, "late")

    def update_calendar(self, year: int, month: int, shifts: dict, employees: dict):
        """
        カレンダー表示を更新する。

        Args:
            year (int): 表示する年。
            month (int): 表示する月。
            shifts (dict): その月のシフトデータ。
            employees (dict): 全社員のデータ (ID -> Employee)。
        """
        self.current_date = datetime.date(year, month, 1)
        self.month_label.setText(f"{year}年 {month}月")

        num_days = calendar.monthrange(year, month)[1]
        self.calendar_table.setRowCount(num_days)

        for day in range(1, num_days + 1):
            date_obj = datetime.date(year, month, day)
            date_str = date_obj.isoformat()

            # 日付アイテム
            day_of_week = ["月", "火", "水", "木", "金", "土", "日"][date_obj.weekday()]
            date_item = QTableWidgetItem(f"{day} ({day_of_week})")
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.calendar_table.setItem(day - 1, 0, date_item)

            # シフトアイテム
            shift = shifts.get(date_str)
            early_shift_name = ""
            late_shift_name = ""

            if shift:
                if shift.early_shift_employee_id in employees:
                    early_shift_name = employees[shift.early_shift_employee_id].name
                if shift.late_shift_employee_id in employees:
                    late_shift_name = employees[shift.late_shift_employee_id].name

            early_item = QTableWidgetItem(early_shift_name)
            late_item = QTableWidgetItem(late_shift_name)
            early_item.setFlags(early_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            late_item.setFlags(late_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.calendar_table.setItem(day - 1, 1, early_item)
            self.calendar_table.setItem(day - 1, 2, late_item)

    def show_error_message(self, title: str, message: str):
        """
        エラーメッセージダイアログを表示する。
        """
        QMessageBox.critical(self, title, message)

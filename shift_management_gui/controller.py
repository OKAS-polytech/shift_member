"""
GUIアプリケーションのコントローラを定義するモジュール。
"""
import datetime
from PyQt6.QtWidgets import QMessageBox
from shift_management.manager import ShiftManager
from .main_window import MainWindow
from .dialogs import EmployeeManagementDialog, SelectEmployeeDialog

class ShiftController:
    """
    Model (ShiftManager) と View (MainWindow) をつなぐコントローラ。
    """
    def __init__(self, manager: ShiftManager, view: MainWindow):
        """
        ShiftControllerを初期化する。

        Args:
            manager (ShiftManager): ビジネスロジックを担うモデル。
            view (MainWindow): UIを担当するビュー。
        """
        self._manager = manager
        self._view = view
        self._current_date = datetime.date.today()

        # --- シグナルとハンドラ（スロット）を接続 ---
        self._connect_signals()

        # --- 初期カレンダー表示 ---
        self.update_calendar_view()

    def _connect_signals(self):
        """
        Viewから発行されるシグナルをコントローラのハンドラに接続する。
        """
        self._view.month_change_requested.connect(self._handle_month_change)
        self._view.manage_employees_requested.connect(self._handle_manage_employees)
        self._view.assign_shift_requested.connect(self._handle_assign_shift)
        self._view.auto_generate_shifts_requested.connect(self._handle_auto_generate_shifts)
        self._view.exit_requested.connect(self._view.close)

    def update_calendar_view(self):
        """
        現在の年月に基づいてカレンダービューを更新する。
        """
        year = self._current_date.year
        month = self._current_date.month

        shifts = self._manager.get_shifts_for_month(year, month)
        employees = {emp.id: emp for emp in self._manager.get_all_employees()}

        self._view.update_calendar(year, month, shifts, employees)

    def _handle_month_change(self, direction: int):
        """
        「前月」「次月」ボタンのリクエストを処理する。

        Args:
            direction (int): -1なら前月、1なら次月。
        """
        # 現在の月の1日を基準に月を計算
        current_month_first_day = self._current_date.replace(day=1)
        # 月の加算・減算（単純な加減算では年末年始などで問題が出るため、安全な方法をとる）
        new_month = current_month_first_day.month + direction
        new_year = current_month_first_day.year
        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1

        self._current_date = self._current_date.replace(year=new_year, month=new_month)
        self.update_calendar_view()

    def _handle_manage_employees(self):
        """
        社員管理メニューのリクエストを処理する。
        """
        employees = self._manager.get_all_employees()
        dialog = EmployeeManagementDialog(employees, self._view)

        # ダイアログからのシグナルを接続
        dialog.add_employee_requested.connect(
            lambda name: self._handle_add_employee(name, dialog)
        )

        dialog.exec()

    def _handle_add_employee(self, name: str, dialog: EmployeeManagementDialog):
        """
        社員追加のリクエストを処理する。
        """
        self._manager.add_employee(name)

        # モデルが変更されたので、ダイアログのリストを更新
        updated_employees = self._manager.get_all_employees()
        dialog.update_employee_list(updated_employees)

        # メインのカレンダーも更新が必要な場合がある (名前の表示など)
        self.update_calendar_view()

    def _handle_assign_shift(self, date: datetime.date, shift_type: str):
        """
        シフト割り当てのリクエストを処理する。
        """
        employees = self._manager.get_all_employees()
        if not employees:
            self._view.show_error_message("エラー", "登録されている社員がいません。")
            return

        dialog = SelectEmployeeDialog(employees, self._view)
        if dialog.exec():
            employee_id = dialog.selected_employee_id
            if employee_id is not None:
                try:
                    self._manager.set_shift(date, shift_type, employee_id)
                    # モデルが変更されたので、カレンダービューを更新
                    self.update_calendar_view()
                except ValueError as e:
                    self._view.show_error_message("エラー", str(e))

    def _handle_auto_generate_shifts(self):
        """
        シフト自動生成のリクエストを処理する。
        """
        reply = QMessageBox.question(
            self._view,
            "確認",
            f"{self._current_date.year}年{self._current_date.month}月のシフトを自動生成しますか？\n"
            "既存のシフトはすべて上書きされます。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                year = self._current_date.year
                month = self._current_date.month
                self._manager.generate_shifts_for_month(year, month)
                self.update_calendar_view()
                QMessageBox.information(self._view, "成功", "シフトが自動生成されました。")
            except ValueError as e:
                self._view.show_error_message("生成エラー", str(e))

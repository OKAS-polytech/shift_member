"""
GUIアプリケーションで使用されるダイアログを定義するモジュール。
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QDialogButtonBox,
    QInputDialog, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List
from shift_management.models import Employee

class EmployeeManagementDialog(QDialog):
    """
    社員の管理（一覧表示、追加）を行うためのダイアログ。
    """
    # --- Signals ---
    # 新しい社員の追加が要求されたときに発行される (社員名)
    add_employee_requested = pyqtSignal(str)

    def __init__(self, employees: List[Employee], parent=None):
        """
        EmployeeManagementDialogを初期化する。

        Args:
            employees (List[Employee]): 表示する社員のリスト。
            parent: 親ウィジェット。
        """
        super().__init__(parent)
        self.setWindowTitle("社員管理")

        self._employees = employees
        self._setup_ui()
        self._populate_employee_list()

    def _setup_ui(self):
        """
        UIコンポーネントを初期化し、レイアウトを設定する。
        """
        layout = QVBoxLayout(self)

        self.employee_list_widget = QListWidget()
        layout.addWidget(self.employee_list_widget)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("社員を追加")
        self.close_button = QPushButton("閉じる")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        # --- シグナルとスロットの接続 ---
        self.add_button.clicked.connect(self._request_add_employee)
        self.close_button.clicked.connect(self.accept)

    def _populate_employee_list(self):
        """
        社員リストウィジェットに現在の社員情報を設定する。
        """
        self.employee_list_widget.clear()
        if not self._employees:
            self.employee_list_widget.addItem("登録されている社員はいません。")
        else:
            for emp in self._employees:
                self.employee_list_widget.addItem(f"ID: {emp.id}, 氏名: {emp.name}")

    def _request_add_employee(self):
        """
        新しい社員を追加するための入力ダイアログを表示し、結果をシグナルで発行する。
        """
        name, ok = QInputDialog.getText(self, "社員の追加", "新しい社員の氏名を入力してください:")
        if ok and name:
            self.add_employee_requested.emit(name)
        elif ok and not name:
            QMessageBox.warning(self, "入力エラー", "氏名が入力されていません。")

    def update_employee_list(self, employees: List[Employee]):
        """
        ダイアログ内の社員リストを更新する。
        コントローラがモデルの変更を検知した後に呼び出す。
        """
        self._employees = employees
        self._populate_employee_list()

class SelectEmployeeDialog(QDialog):
    """
    シフトに割り当てる社員を選択するためのダイアログ。
    """
    def __init__(self, employees: List[Employee], parent=None):
        """
        SelectEmployeeDialogを初期化する。
        """
        super().__init__(parent)
        self.setWindowTitle("社員の選択")

        self.selected_employee_id = None

        layout = QVBoxLayout(self)
        self.employee_list = QListWidget()
        for emp in employees:
            item = QListWidgetItem(f"{emp.name} (ID: {emp.id})")
            item.setData(Qt.ItemDataRole.UserRole, emp.id)
            self.employee_list.addItem(item)
        layout.addWidget(self.employee_list)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        """
        OKボタンがクリックされたときの処理。
        選択された社員のIDを保存する。
        """
        selected_items = self.employee_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "選択エラー", "社員を選択してください。")
            return

        self.selected_employee_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        super().accept()

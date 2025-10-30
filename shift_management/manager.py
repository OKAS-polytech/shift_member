"""
シフト管理アプリケーションのビジネスロジックを管理するモジュール。
"""
import datetime
import json
import os
from typing import Dict, List, Optional

from .models import Employee, Shift

class ShiftManager:
    """
    社員とシフト情報を管理し、データの永続化を行うクラス。
    """
    def __init__(self, data_dir: str = "data"):
        """
        ShiftManagerを初期化する。

        Args:
            data_dir (str): データファイルを保存するディレクトリ。
        """
        self.data_dir = data_dir
        self.employees_file = os.path.join(data_dir, "employees.json")
        self.shifts_file = os.path.join(data_dir, "shifts.json")

        self._employees: Dict[int, Employee] = {}
        self._shifts: Dict[str, Shift] = {}  # "YYYY-MM-DD" -> Shift

        self.load_data()

    def load_data(self):
        """
        ファイルから社員とシフトの情報を読み込む。
        """
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        if os.path.exists(self.employees_file):
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                employees_data = json.load(f)
                for emp in employees_data:
                    self._employees[emp['id']] = Employee(**emp)

        if os.path.exists(self.shifts_file):
            with open(self.shifts_file, 'r', encoding='utf-8') as f:
                shifts_data = json.load(f)
                for date_str, shift_data in shifts_data.items():
                    shift_data['date'] = datetime.date.fromisoformat(shift_data['date'])
                    self._shifts[date_str] = Shift(**shift_data)

    def save_data(self):
        """
        現在の社員とシフトの情報をファイルに保存する。
        """
        with open(self.employees_file, 'w', encoding='utf-8') as f:
            employees_data = [emp.__dict__ for emp in self._employees.values()]
            json.dump(employees_data, f, indent=4, ensure_ascii=False)

        with open(self.shifts_file, 'w', encoding='utf-8') as f:
            shifts_data_to_save = {}
            for date_str, shift in self._shifts.items():
                shift_dict = shift.__dict__.copy()
                shift_dict['date'] = shift.date.isoformat()
                shifts_data_to_save[date_str] = shift_dict
            json.dump(shifts_data_to_save, f, indent=4, ensure_ascii=False)

    def add_employee(self, name: str) -> Employee:
        """
        新しい社員を登録する。

        Args:
            name (str): 社員の氏名。

        Returns:
            Employee: 登録された社員オブジェクト。
        """
        new_id = max(self._employees.keys()) + 1 if self._employees else 1
        new_employee = Employee(id=new_id, name=name)
        self._employees[new_id] = new_employee
        self.save_data()
        return new_employee

    def get_all_employees(self) -> List[Employee]:
        """
        登録されている全ての社員情報を取得する。

        Returns:
            List[Employee]: 社員オブジェクトのリスト。
        """
        return list(self._employees.values())

    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        IDで社員を検索する。

        Args:
            employee_id (int): 検索する社員のID。

        Returns:
            Optional[Employee]: 見つかった社員オブジェクト。見つからなければNone。
        """
        return self._employees.get(employee_id)

    def set_shift(self, date: datetime.date, shift_type: str, employee_id: int):
        """
        特定の日付とシフトに社員を割り当てる。

        Args:
            date (datetime.date): 割り当てる日付。
            shift_type (str): "early" または "late"。
            employee_id (int): 割り当てる社員のID。

        Raises:
            ValueError: shift_typeが不正な場合、またはemployee_idが存在しない場合。
        """
        if employee_id not in self._employees:
            raise ValueError("指定されたIDの社員は存在しません。")

        date_str = date.isoformat()
        shift = self._shifts.get(date_str)
        if not shift:
            shift = Shift(date=date)
            self._shifts[date_str] = shift

        if shift_type == "early":
            shift.early_shift_employee_id = employee_id
        elif shift_type == "late":
            shift.late_shift_employee_id = employee_id
        else:
            raise ValueError("シフトタイプは 'early' または 'late' を指定してください。")

        self.save_data()

    def get_shifts_for_month(self, year: int, month: int) -> Dict[str, Shift]:
        """
        指定した年月のシフト情報を取得する。

        Args:
            year (int): 年。
            month (int): 月。

        Returns:
            Dict[str, Shift]: その月のシフト情報の辞書 ("YYYY-MM-DD" -> Shift)。
        """
        return {
            date_str: shift for date_str, shift in self._shifts.items()
            if shift.date.year == year and shift.date.month == month
        }

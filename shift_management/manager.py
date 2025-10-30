"""
シフト管理アプリケーションのビジネスロジックを管理するモジュール。
"""
import datetime
import json
import os
import calendar
import random
from itertools import cycle
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
                    # 古いデータ形式との互換性のための処理
                    if 'desired_holidays' not in emp:
                        emp['desired_holidays'] = 8  # デフォルト値
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

    def add_employee(self, name: str, desired_holidays: int = 8) -> Employee:
        """
        新しい社員を登録する。

        Args:
            name (str): 社員の氏名。
            desired_holidays (int): 希望休日数。

        Returns:
            Employee: 登録された社員オブジェクト。
        """
        new_id = max(self._employees.keys()) + 1 if self._employees else 1
        new_employee = Employee(id=new_id, name=name, desired_holidays=desired_holidays)
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

    def generate_shifts_with_constraints(self, year: int, month: int, max_consecutive_work: int):
        """
        制約（希望休日数、最大連勤日数）に基づいてシフトを生成する。
        """
        employees = self.get_all_employees()
        num_days = calendar.monthrange(year, month)[1]

        # --- 事前チェック ---
        total_shifts_needed = num_days * 2  # 早番 + 遅番
        total_work_days_available = sum(num_days - emp.desired_holidays for emp in employees)
        if total_shifts_needed > total_work_days_available:
            raise ValueError("全社員の合計勤務可能日数では、全てのシフトを埋めることができません。")

        # --- 内部状態の初期化 ---
        work_counts = {emp.id: 0 for emp in employees}
        holiday_counts = {emp.id: 0 for emp in employees}
        consecutive_work_counts = {emp.id: 0 for emp in employees}

        # 既存シフトのクリア
        date_strs_to_delete = [
            d_str for d_str, s in self._shifts.items() if s.date.year == year and s.date.month == month
        ]
        for d_str in date_strs_to_delete:
            del self._shifts[d_str]

        # --- シフト割り当て ---
        for day in range(1, num_days + 1):
            date = datetime.date(year, month, day)
            shift = Shift(date=date)

            # --- ヘルパー: 割り当て候補者を決定 ---
            def find_candidate(assigned_in_shift: List[int]) -> int:
                candidates = []
                for emp in employees:
                    emp_id = emp.id
                    # 既に同じ日に割り当てられていない
                    if emp_id in assigned_in_shift: continue
                    # 連勤上限に達していない
                    if consecutive_work_counts[emp_id] >= max_consecutive_work: continue
                    # 勤務日数が上限（月の日数 - 希望休）に達していない
                    if work_counts[emp_id] >= num_days - emp.desired_holidays: continue
                    candidates.append(emp)

                if not candidates:
                    raise ValueError(f"{date}のシフト割り当てに失敗しました。条件を満たす社員がいません。")

                # 優先度: (勤務日数が少ない > ランダム) - 昇順ソート
                candidates.sort(key=lambda e: (
                    work_counts[e.id],
                    random.random()
                ))
                return candidates[0].id

            # --- 早番・遅番の割り当て ---
            assigned_today = []

            early_emp_id = find_candidate(assigned_today)
            shift.early_shift_employee_id = early_emp_id
            work_counts[early_emp_id] += 1
            consecutive_work_counts[early_emp_id] += 1
            assigned_today.append(early_emp_id)

            late_emp_id = find_candidate(assigned_today)
            shift.late_shift_employee_id = late_emp_id
            work_counts[late_emp_id] += 1
            consecutive_work_counts[late_emp_id] += 1

            self._shifts[date.isoformat()] = shift

            # --- 休日と連勤カウントの更新 ---
            for emp in employees:
                if emp.id not in [early_emp_id, late_emp_id]:
                    holiday_counts[emp.id] += 1
                    consecutive_work_counts[emp.id] = 0 # 休みでリセット

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

    def generate_shifts_for_month(self, year: int, month: int):
        """
        指定された月のシフトを自動的に生成する。

        このメソッドは、登録されている全社員を使用して、毎日早番と遅番に
        一人ずつ順番に割り当てます。
        少なくとも2人の社員が登録されている必要があります。

        Args:
            year (int): 対象の年。
            month (int): 対象の月。

        Raises:
            ValueError: 登録社員が2人未満の場合。
        """
        employees = self.get_all_employees()
        if len(employees) < 2:
            raise ValueError("シフトを自動生成するには、少なくとも2人の社員が必要です。")

        # 既存の月のシフトをクリア
        date_strs_to_delete = [
            date_str for date_str, shift in self._shifts.items()
            if shift.date.year == year and shift.date.month == month
        ]
        for date_str in date_strs_to_delete:
            del self._shifts[date_str]

        num_days = calendar.monthrange(year, month)[1]
        employee_ids = [emp.id for emp in employees]
        num_employees = len(employee_ids)

        # ラウンドロビン用のインデックス
        early_idx = 0
        late_idx = 1  # 早番と遅番が同じ人にならないようにオフセット

        for day in range(1, num_days + 1):
            date = datetime.date(year, month, day)
            date_str = date.isoformat()

            shift = Shift(date=date)
            shift.early_shift_employee_id = employee_ids[early_idx % num_employees]
            shift.late_shift_employee_id = employee_ids[late_idx % num_employees]

            self._shifts[date_str] = shift

            # インデックスを更新
            early_idx += 1
            late_idx += 1

        self.save_data()

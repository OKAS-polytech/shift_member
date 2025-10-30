"""
シフト管理アプリケーションのモデルクラスを定義するモジュール。
"""
import datetime
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Employee:
    """
    社員情報を表現するデータクラス。

    Attributes:
        id (int): 一意の識別子。
        name (str): 社員の氏名。
        desired_holidays (int): 1ヶ月あたりの希望休日数。
    """
    id: int
    name: str
    desired_holidays: int = 8

@dataclass
class Shift:
    """
    特定の日付のシフト情報を表現するデータクラス。

    Attributes:
        date (datetime.date): 対象の日付。
        early_shift_employee_id (Optional[int]): 早番を担当する社員のID。デフォルトはNone。
        late_shift_employee_id (Optional[int]): 遅番を担当する社員のID。デフォルトはNone。
    """
    date: datetime.date
    early_shift_employee_id: Optional[int] = None
    late_shift_employee_id: Optional[int] = None

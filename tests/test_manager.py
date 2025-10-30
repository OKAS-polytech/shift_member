"""
`ShiftManager` クラスの単体テスト。
"""
import datetime
import os
import json
import pytest
from shift_management.manager import ShiftManager
from shift_management.models import Employee, Shift

@pytest.fixture
def temp_data_dir(tmp_path):
    """
    テスト用の一次的なデータディレクトリを提供するpytestフィクスチャ。
    """
    return tmp_path

def test_add_employee(temp_data_dir):
    """
    社員の追加機能が正しく動作することをテストする。
    """
    manager = ShiftManager(data_dir=str(temp_data_dir))

    # 1. 最初の社員を追加
    employee1 = manager.add_employee("山田 太郎")
    assert employee1.id == 1
    assert employee1.name == "山田 太郎"

    employees = manager.get_all_employees()
    assert len(employees) == 1
    assert employees[0].name == "山田 太郎"

    # 2. 2人目の社員を追加
    employee2 = manager.add_employee("鈴木 花子")
    assert employee2.id == 2
    assert employee2.name == "鈴木 花子"

    employees = manager.get_all_employees()
    assert len(employees) == 2

def test_data_persistence(temp_data_dir):
    """
    データがファイルに正しく永続化され、再読み込みされることをテストする。
    """
    data_dir = str(temp_data_dir)

    # 1. データをセットアップして保存
    manager1 = ShiftManager(data_dir=data_dir)
    manager1.add_employee("佐藤 一郎")
    test_date = datetime.date(2025, 1, 10)
    manager1.set_shift(test_date, "early", 1)

    # 2. 別のマネージャーインスタンスでデータを読み込む
    manager2 = ShiftManager(data_dir=data_dir)

    # 社員情報がロードされたか確認
    employees = manager2.get_all_employees()
    assert len(employees) == 1
    assert employees[0].id == 1
    assert employees[0].name == "佐藤 一郎"

    # シフト情報がロードされたか確認
    shifts = manager2.get_shifts_for_month(2025, 1)
    date_str = test_date.isoformat()
    assert date_str in shifts
    assert shifts[date_str].early_shift_employee_id == 1
    assert shifts[date_str].late_shift_employee_id is None

def test_set_shift(temp_data_dir):
    """
    シフトの割り当て機能が正しく動作することをテストする。
    """
    manager = ShiftManager(data_dir=str(temp_data_dir))
    emp1 = manager.add_employee("社員A")
    emp2 = manager.add_employee("社員B")

    test_date = datetime.date(2025, 5, 20)

    # 1. 早番を割り当て
    manager.set_shift(test_date, "early", emp1.id)

    shifts_month = manager.get_shifts_for_month(2025, 5)
    shift = shifts_month[test_date.isoformat()]

    assert shift.date == test_date
    assert shift.early_shift_employee_id == emp1.id
    assert shift.late_shift_employee_id is None

    # 2. 遅番を割り当て (既存のシフトを更新)
    manager.set_shift(test_date, "late", emp2.id)

    shifts_month_updated = manager.get_shifts_for_month(2025, 5)
    shift_updated = shifts_month_updated[test_date.isoformat()]

    assert shift_updated.early_shift_employee_id == emp1.id
    assert shift_updated.late_shift_employee_id == emp2.id

def test_set_shift_with_invalid_employee(temp_data_dir):
    """
    存在しない社員IDでシフトを割り当てようとするとValueErrorが発生することをテストする。
    """
    manager = ShiftManager(data_dir=str(temp_data_dir))
    test_date = datetime.date(2025, 1, 1)

    with pytest.raises(ValueError, match="指定されたIDの社員は存在しません。"):
        manager.set_shift(test_date, "early", 999)

def test_get_shifts_for_month(temp_data_dir):
    """
    指定した月のシフトのみが取得されることをテストする。
    """
    manager = ShiftManager(data_dir=str(temp_data_dir))
    emp = manager.add_employee("テスト社員")

    # 異なる月のシフトを作成
    date_march = datetime.date(2025, 3, 15)
    date_april = datetime.date(2025, 4, 1)

    manager.set_shift(date_march, "early", emp.id)
    manager.set_shift(date_april, "late", emp.id)

    # 3月のシフトを取得
    shifts_march = manager.get_shifts_for_month(2025, 3)
    assert len(shifts_march) == 1
    assert date_march.isoformat() in shifts_march

    # 4月のシフトを取得
    shifts_april = manager.get_shifts_for_month(2025, 4)
    assert len(shifts_april) == 1
    assert date_april.isoformat() in shifts_april

    # シフトがない月は空の辞書が返される
    shifts_may = manager.get_shifts_for_month(2025, 5)
    assert len(shifts_may) == 0

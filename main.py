"""
CUIシフト管理アプリケーションのエントリーポイント。
"""
import datetime
import calendar
from shift_management.manager import ShiftManager
from shift_management.models import Employee

class Application:
    """
    CUIアプリケーションの実行を管理するクラス。
    """
    def __init__(self):
        """
        Applicationを初期化する。
        """
        self.manager = ShiftManager()

    def run(self):
        """
        アプリケーションのメインループを実行する。
        """
        while True:
            self._show_main_menu()
            choice = input("操作を選択してください: ")
            if choice == '1':
                self._manage_employees()
            elif choice == '2':
                self._manage_shifts()
            elif choice == '3':
                print("アプリケーションを終了します。")
                break
            else:
                print("無効な選択です。もう一度入力してください。")

    def _show_main_menu(self):
        """
        メインメニューを表示する。
        """
        print("\n--- シフト管理アプリケーション ---")
        print("1. 社員管理")
        print("2. シフト管理")
        print("3. 終了")

    def _manage_employees(self):
        """
        社員管理メニューを処理する。
        """
        while True:
            print("\n--- 社員管理 ---")
            print("1. 社員を登録する")
            print("2. 社員一覧を表示する")
            print("3. メインメニューに戻る")
            choice = input("操作を選択してください: ")
            if choice == '1':
                self._add_employee()
            elif choice == '2':
                self._list_employees()
            elif choice == '3':
                break
            else:
                print("無効な選択です。")

    def _add_employee(self):
        """
        新しい社員を登録する。
        """
        name = input("新しい社員の氏名を入力してください: ")
        if name:
            employee = self.manager.add_employee(name)
            print(f"{employee.name}さんを登録しました。")
        else:
            print("氏名が入力されていません。")

    def _list_employees(self):
        """
        登録されている社員の一覧を表示する。
        """
        employees = self.manager.get_all_employees()
        print("\n--- 登録社員一覧 ---")
        if not employees:
            print("登録されている社員はいません。")
        else:
            for emp in employees:
                print(f"- ID: {emp.id}, 氏名: {emp.name}")

    def _manage_shifts(self):
        """
        シフト管理メニューを処理する。
        """
        while True:
            print("\n--- シフト管理 ---")
            print("1. シフトを作成・編集する")
            print("2. シフトを表示する")
            print("3. メインメニューに戻る")
            choice = input("操作を選択してください: ")
            if choice == '1':
                self._edit_shift()
            elif choice == '2':
                self._view_shifts()
            elif choice == '3':
                break
            else:
                print("無効な選択です。")

    def _edit_shift(self):
        """
        シフトを作成または編集する。
        """
        year_month_str = input("シフトを編集する年月を入力してください (例: 202304): ")
        try:
            year = int(year_month_str[:4])
            month = int(year_month_str[4:])
            _, num_days = calendar.monthrange(year, month)
        except (ValueError, TypeError):
            print("不正なフォーマットです。")
            return

        day_str = input(f"日付を選択してください (1-{num_days}): ")
        try:
            day = int(day_str)
            target_date = datetime.date(year, month, day)
        except (ValueError, TypeError):
            print("不正な日付です。")
            return

        shift_type_str = input("シフトを選択してください (1: 早番, 2: 遅番): ")
        if shift_type_str == '1':
            shift_type = "early"
        elif shift_type_str == '2':
            shift_type = "late"
        else:
            print("無効な選択です。")
            return

        employees = self.manager.get_all_employees()
        if not employees:
            print("登録されている社員がいません。まず社員を登録してください。")
            return

        print("担当する社員を選択してください:")
        for emp in employees:
            print(f"{emp.id}. {emp.name}")

        emp_id_str = input("社員番号を選択してください: ")
        try:
            emp_id = int(emp_id_str)
            if not self.manager.get_employee_by_id(emp_id):
                print("存在しない社員番号です。")
                return
            self.manager.set_shift(target_date, shift_type, emp_id)
            print(f"{target_date.strftime('%Y年%m月%d日')}の{ '早番' if shift_type == 'early' else '遅番' }に社員番号{emp_id}の方を割り当てました。")
        except ValueError as e:
            print(f"エラー: {e}")
        except TypeError:
            print("不正な社員番号です。")


    def _view_shifts(self):
        """
        指定された年月のシフト表を表示する。
        """
        year_month_str = input("表示する年月を入力してください (例: 202304): ")
        try:
            year = int(year_month_str[:4])
            month = int(year_month_str[4:])
        except (ValueError, TypeError):
            print("不正なフォーマットです。")
            return

        shifts = self.manager.get_shifts_for_month(year, month)
        employees = {emp.id: emp for emp in self.manager.get_all_employees()}

        print(f"\n--- {year}年{month}月 シフト表 ---")
        print("日付 | 早番       | 遅番")
        print("----------------------------------")

        _, num_days = calendar.monthrange(year, month)
        for day in range(1, num_days + 1):
            date = datetime.date(year, month, day)
            date_str = date.isoformat()

            shift = shifts.get(date_str)
            early_shift_emp_name = "(未割り当て)"
            late_shift_emp_name = "(未割り当て)"

            if shift:
                if shift.early_shift_employee_id and shift.early_shift_employee_id in employees:
                    early_shift_emp_name = employees[shift.early_shift_employee_id].name
                if shift.late_shift_employee_id and shift.late_shift_employee_id in employees:
                    late_shift_emp_name = employees[shift.late_shift_employee_id].name

            print(f"{day:2d}   | {early_shift_emp_name:<10} | {late_shift_emp_name:<10}")

if __name__ == "__main__":
    app = Application()
    app.run()

# 3. 内部設計書

## 3.1. 概要

本ドキュメントは、シフト管理アプリケーションの内部設計を定義する。
クラス構造、データ構造、および各クラスの責務について記述する。

## 3.2. クラス設計

アプリケーションは、以下のクラスで構成される。

- `Employee`: 社員情報を保持するモデルクラス。
- `Shift`: 特定の日付のシフト情報を保持するモデルクラス。
- `ShiftManager`: 社員とシフトの管理、データの永続化を行うクラス。
- `Application`: CUIの表示とユーザー入力を処理し、アプリケーション全体を制御するクラス。

### 3.2.1. `Employee` クラス (`shift_management/models.py`)

- **責務**: 一人の社員情報を表現する。
- **プロパティ**:
  - `id` (int): 一意の識別子。
  - `name` (str): 社員の氏名。

### 3.2.2. `Shift` クラス (`shift_management/models.py`)

- **責務**: 特定の日付における早番・遅番の担当者を表現する。
- **プロパティ**:
  - `date` (datetime.date): 対象の日付。
  - `early_shift_employee_id` (int, optional): 早番を担当する社員のID。
  - `late_shift_employee_id` (int, optional): 遅番を担当する社員のID。

### 3.2.3. `ShiftManager` クラス (`shift_management/manager.py`)

- **責務**: ビジネスロジック全体を管理する。社員とシフトのCRUD（作成、読み取り、更新、削除）操作、およびデータの永続化を担当する。
- **メソッド**:
  - `add_employee(name: str)`: 新しい社員を登録する。
  - `get_all_employees() -> list[Employee]`: 全ての社員情報を取得する。
  - `set_shift(date: datetime.date, shift_type: str, employee_id: int)`: 特定の日付とシフトに社員を割り当てる。
  - `get_shifts_for_month(year: int, month: int) -> dict[datetime.date, Shift]`: 指定した年月のシフト情報を取得する。
  - `save_data()`: 現在の社員とシフトの情報をファイルに保存する。
  - `load_data()`: ファイルから社員とシフトの情報を読み込む。
- **データ永続化**:
  - 社員データは `data/employees.json` に保存する。
  - シフトデータは `data/shifts.json` に保存する。
  - 形式はJSONとする。

### 3.2.4. `Application` クラス (`main.py`)

- **責務**: ユーザーインターフェースを提供し、ユーザーの入力を受け付けて `ShiftManager` の適切なメソッドを呼び出す。
- **メソッド**:
  - `run()`: アプリケーションのメインループを実行する。
  - `_show_main_menu()`: メインメニューを表示し、入力を受け付ける。
  - `_manage_employees()`: 社員管理メニューのロジックを処理する。
  - `_manage_shifts()`: シフト管理メニューのロジックを処理する。

## 3.3. ディレクトリ構造

最終的なディレクトリ構造は以下のようになる。

```
.
├── doc/
│   ├── 01_requirements_definition.md
│   ├── 02_external_design.md
│   └── 03_internal_design.md
├── shift_management/
│   ├── __init__.py
│   ├── models.py
│   └── manager.py
├── data/
│   ├── employees.json
│   └── shifts.json
└── main.py
```

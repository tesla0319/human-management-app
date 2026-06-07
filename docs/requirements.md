# 人材管理アプリ MVP 要件書

## 概要

社員情報を管理するWebアプリケーション。

## 技術スタック

- Backend: Python, FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Testing: pytest

## MVP機能

### 1. 社員一覧 (List Employees)
- 全社員を一覧表示
- REST: `GET /api/employees`
- 応答: 社員情報の配列

### 2. 社員登録 (Create Employee)
- 新規社員を追加
- REST: `POST /api/employees`
- リクエスト: name, department, role, skill_summary, joined_date, active

### 3. 社員詳細 (Get Employee)
- 指定社員の詳細情報を取得
- REST: `GET /api/employees/{id}`
- 応答: 社員情報オブジェクト

### 4. 社員編集 (Update Employee)
- 社員情報を更新
- REST: `PUT /api/employees/{id}`
- リクエスト: name, department, role, skill_summary, joined_date, active

### 5. 社員削除 (Delete Employee)
- 社員情報を削除
- REST: `DELETE /api/employees/{id}`

### 6. 部署検索 (Search by Department)
- 指定した部署の社員のみを取得
- REST: `GET /api/employees?department={department}`
- 応答: 社員情報の配列（該当なしの場合は空配列）

### 7. スキル・経験・職種によるマッチング検索 (Match Employees)
- スキル・開発経験・職種を条件に社員を検索
- REST: `GET /api/employees/match`
- クエリパラメータ: skill（複数指定・AND/OR切替: skill_match）, experience, role
- 応答: 条件に一致した社員情報の配列

### 8. スキル集計 (Skill Summary)
- 全社員のskill_summaryを集計し、スキルごとの保有人数を取得
- REST: `GET /api/skills/summary`
- 応答: スキル名と人数のマップ

### 9. スキル別経験年数管理 (Employee Skills)
- 社員ごとにスキル名と経験年数を構造化データとして登録・取得・更新・削除
- REST:
  - `POST /api/employees/{employee_id}/skills`
  - `GET /api/employees/{employee_id}/skills`
  - `PUT /api/employees/{employee_id}/skills/{skill_id}`
  - `DELETE /api/employees/{employee_id}/skills/{skill_id}`
- 既存のskill_summary（自由記述）とは独立した構造化データとして管理する

## データモデル

### Employee テーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | Integer | 主キー (自動採番) |
| name | String | 社員名 (必須) |
| department | String | 部門 (必須) |
| role | String | 職種 (必須) |
| skill_summary | String | スキル概要 (必須) |
| joined_date | Date | 入社日 (必須) |
| active | Boolean | 在籍状態 (必須, デフォルト: True) |

### EmployeeSkill テーブル (employee_skills)

| カラム | 型 | 説明 |
|--------|------|------|
| id | Integer | 主キー (自動採番) |
| employee_id | Integer | Employee.id への外部キー (必須) |
| skill_name | String | スキル名 (必須) |
| years | Integer | 経験年数 (必須, デフォルト: 0) |

- employee_id + skill_name の組み合わせに一意制約
- skill_summary（自由記述）とは独立した構造化データとして管理する

## 対象外

- ログイン認証
- 権限管理
- AI機能
- ファイルアップロード
- Docker
- クラウドデプロイ

## テスト方針

- pytest を使用したユニットテスト
- 各 API エンドポイントのテスト実装

## API仕様

### ベースURL
`http://localhost:8000/api`

### レスポンス形式
JSON

### エラーハンドリング
- 404: リソースが見つからない
- 422: リクエストバリデーションエラー（必須項目欠如、型不正、空文字など）
- 409: 重複（同一社員内で同じスキル名が既に登録されている場合など）
- 500: サーバーエラー

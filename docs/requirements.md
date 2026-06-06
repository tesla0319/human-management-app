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
- 400: リクエスト不正
- 500: サーバーエラー

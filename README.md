# 人材管理アプリ MVP

社員情報をCRUD管理するREST API。

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.x |
| フレームワーク | FastAPI |
| データ管理 | インメモリ（起動中のみ保持） |
| テスト | pytest |

## セットアップ

```bash
# 仮想環境の作成・有効化
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存パッケージのインストール
pip install fastapi uvicorn pytest httpx
```

## 起動

```bash
uvicorn app.main:app --reload
```

起動後、以下のURLでAPIドキュメントを確認できます。

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## テスト実行

```bash
pytest
```

現在 **14件** のテストがあります。

## API一覧

ベースURL: `http://localhost:8000`

### 社員登録

```
POST /api/employees
```

リクエストボディ:

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| name | string | ✓ | 社員名（空文字不可） |
| department | string | ✓ | 部門 |
| role | string | ✓ | 職種 |
| skill_summary | string | ✓ | スキル概要 |
| joined_date | date | ✓ | 入社日（YYYY-MM-DD） |
| active | boolean | | 在籍状態（デフォルト: true） |

レスポンス: `201 Created` — 登録した社員情報

---

### 社員一覧取得

```
GET /api/employees
```

レスポンス: `200 OK` — 社員情報の配列

---

### 社員詳細取得

```
GET /api/employees/{employee_id}
```

レスポンス: `200 OK` — 指定IDの社員情報  
存在しないIDの場合: `404 Not Found`

---

### 社員更新

```
PUT /api/employees/{employee_id}
```

リクエストボディ: 社員登録と同じフィールド

レスポンス: `200 OK` — 更新後の社員情報  
存在しないIDの場合: `404 Not Found`

---

### 社員削除

```
DELETE /api/employees/{employee_id}
```

レスポンス: `204 No Content`  
存在しないIDの場合: `404 Not Found`

## レスポンス形式（Employee）

```json
{
  "id": 1,
  "name": "田中太郎",
  "department": "営業部",
  "role": "営業",
  "skill_summary": "営業スキル、顧客対応",
  "joined_date": "2024-01-01",
  "active": true
}
```

## 現時点の制約

- **DB永続化なし** — サーバー再起動でデータはリセットされる
- **認証なし** — 全エンドポイントが認証なしでアクセス可能
- **画面なし** — APIのみ提供（UIは対象外）

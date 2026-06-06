# 人材管理アプリ MVP

社員情報をCRUD管理するREST API。スキル・経験によるマッチング検索にも対応。

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

現在 **23件** のテストがあります。

## API一覧

ベースURL: `http://localhost:8000`

### スキル・経験マッチング検索

```
GET /api/employees/match
```

クエリパラメータ:

| パラメータ | 型 | 説明 | マッチ方式 |
|------------|------|------|------|
| skill | string | 保有スキルで絞り込む | `skill_summary` に部分一致 |
| experience | string | 開発経験で絞り込む | `skill_summary` に部分一致 |
| role | string | 職種で絞り込む | `role` に完全一致 |

- 複数パラメータを指定した場合は **AND条件** で絞り込む
- パラメータ未指定の場合は全社員を返す
- 該当なしの場合は空配列を返す

`skill_summary` は保有スキル・開発経験の自由記述欄として利用する。  
例: `"Python, FastAPI, Docker"` のように記入し、`skill=Python` や `experience=Docker` で部分一致検索できる。

レスポンス: `200 OK` — 条件に一致した社員情報の配列

---

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
| skill_summary | string | ✓ | 保有スキル・開発経験の自由記述（例: `"Python, FastAPI, Docker"`） |
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

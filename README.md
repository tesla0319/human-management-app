# 人材管理アプリ MVP

社員情報をCRUD管理するREST API。スキル・経験・職種によるマッチング検索やスキル集計にも対応し、データはSQLiteに永続化される。

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.x |
| フレームワーク | FastAPI |
| データ管理 | SQLite（SQLAlchemy経由で永続化） |
| テスト | pytest |

## セットアップ

```bash
# 仮想環境の作成・有効化
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存パッケージのインストール
pip install fastapi uvicorn pytest httpx sqlalchemy
```

## 起動

```bash
uvicorn app.main:app --reload
```

起動後、以下のURLでAPIドキュメントを確認できます。

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### データベースについて

初回起動時にプロジェクトルートへ SQLiteファイル `employees.db` が自動生成され、社員データはここに保存されます。アプリを再起動してもデータは保持されます。

`employees.db` は `.gitignore` に登録されており、git管理対象外です（各自の環境で自動生成されるため、コミット不要・コミット不可）。

## テスト実行

```bash
pytest
```

現在 **60件** のテストがあります。

## API一覧

ベースURL: `http://localhost:8000`

### スキル・経験マッチング検索

```
GET /api/employees/match
```

クエリパラメータ:

| パラメータ | 型 | 説明 | マッチ方式 |
|------------|------|------|------|
| skill | string（複数指定可） | 保有スキルで絞り込む | `skill_summary` に部分一致 |
| skill_match | string（`and` / `or`、デフォルト: `and`） | `skill`を複数指定した場合の結合方法 | - |
| experience | string | 開発経験で絞り込む | `skill_summary` に部分一致 |
| role | string | 職種で絞り込む | `role` に完全一致 |

- `skill`は `?skill=Python&skill=FastAPI` のように複数指定できる。`skill_match=and`なら指定した全スキル、`skill_match=or`ならいずれかのスキルを保有する社員に絞り込む
- `skill`/`experience`/`role`など異なる種類のパラメータを併用した場合は **AND条件** で絞り込む
- `skill_match`に`and`/`or`以外の値を指定した場合は `422 Unprocessable Entity`
- パラメータ未指定の場合は全社員を返す
- 該当なしの場合は空配列を返す

`skill_summary` は保有スキル・開発経験の自由記述欄として利用する。  
例: `"Python, FastAPI, Docker"` のように記入し、`skill=Python` や `experience=Docker` で部分一致検索できる。

レスポンス: `200 OK` — 条件に一致した社員情報の配列

---

### スキル集計

```
GET /api/skills/summary
```

全社員の `skill_summary` をカンマ区切りで分解し、スキルごとの保有人数を集計する。

- 同一社員内で同じスキルが重複していても1人として数える
- 各項目の前後の空白は除去して集計する

レスポンス: `200 OK` — 例: `{"Python": 2, "FastAPI": 1, "Docker": 1}`

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

### 社員一覧取得・部署検索

```
GET /api/employees
```

クエリパラメータ:

| パラメータ | 型 | 必須 | 説明 |
|------------|------|------|------|
| department | string | | 指定した部署の社員のみに絞り込む（完全一致） |

- `department` 未指定の場合は全社員を返す
- 該当なしの場合は空配列を返す

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

---

### スキル別経験年数管理（employee_skills）

社員ごとに「スキル名」と「経験年数」を構造化データとして登録・取得・更新・削除できる。`skill_summary`（自由記述）とは独立して管理される。

```
POST   /api/employees/{employee_id}/skills
GET    /api/employees/{employee_id}/skills
PUT    /api/employees/{employee_id}/skills/{skill_id}
DELETE /api/employees/{employee_id}/skills/{skill_id}
```

リクエストボディ（POST/PUT共通）:

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| skill_name | string | ✓ | スキル名（空文字不可） |
| years | integer | ✓ | 経験年数（0以上） |

- `years=0` は「該当スキルを保有しているが、経験1年未満」を表す。スキルを保有していない場合は `years=0` ではなく、`employee_skills` にレコードが存在しない状態で表す
- マッチング検索（`GET /api/employees/match`）で `skill=Python` のようにスキル名のみを指定した場合は、経験年数に関わらずPython保有者が対象となる。経験年数を条件にしたい場合は `skill_requirements=Python:0`（保有者全員、1年未満を含む）や `skill_requirements=Python:3`（3年以上）のように指定する
- 同一社員内で同じ`skill_name`を重複登録した場合は `409 Conflict`
- 存在しない`employee_id`または`skill_id`を指定した場合は `404 Not Found`
- 必須項目の欠如や不正な値（空文字、負の値など）の場合は `422 Unprocessable Entity`

レスポンス:

| メソッド | 成功時のステータス | 内容 |
|------|------|------|
| POST | `201 Created` | 登録したスキル情報 |
| GET | `200 OK` | スキル情報の配列（0件の場合は空配列） |
| PUT | `200 OK` | 更新後のスキル情報 |
| DELETE | `204 No Content` | （ボディなし） |

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

## レスポンス形式（EmployeeSkill）

```json
{
  "id": 1,
  "employee_id": 1,
  "skill_name": "Python",
  "years": 3
}
```

## 現時点の制約

- **認証なし** — 全エンドポイントが認証なしでアクセス可能
- **画面なし** — APIのみ提供（UIは対象外）

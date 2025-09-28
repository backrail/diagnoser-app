# 診断アプリ作成キット（Flask）

だれでも「質問・選択肢・結果」を管理画面からカスタマイズして作れる、
診断アプリのスターターです。VS Code を想定。

## クイックスタート

```bash
# 1) 仮想環境（任意）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) 依存関係
pip install -r requirements.txt

# 3) .env 作成
cp .env.example .env
# 必要なら ADMIN_PASSWORD を変更

# 4) 初期データ投入
flask --app app seed

# 5) 起動
flask --app app run --debug
```

- アプリ: http://127.0.0.1:5000/
- 管理画面: http://127.0.0.1:5000/admin  （ユーザー名: admin, パスワード: .env の ADMIN_PASSWORD）

## フォルダ構成

```
diagnoser/
  app.py
  config.py
  extensions.py
  models.py
  blueprints/
    public/routes.py
    admin/routes.py
    __init__.py
  templates/
    base.html
    public/*.html
    admin/*.html
  static/
    css/main.css
    js/main.js
  seed.py
  requirements.txt
  ruff.toml
  .env.example
```

## 仕組み（ざっくり）

- **Quiz / Trait / Question / Choice / ChoiceScore / Result** を SQLite で管理。
- Choice には Trait ごとの点数を紐づけ可能（例: Aの選択で「外向性」に+2）。
- 診断実行時は各 Trait の合計点を算出し、**最大スコアの Trait に紐づく Result** を表示（シンプルな「Max Trait」ロジック）。
- 必要に応じて `models.py` の `ResultRule` や判定関数を拡張してください。

## Ruff

Ruff の軽い設定を `ruff.toml` に同梱しています。

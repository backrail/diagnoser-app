from __future__ import annotations

import os
from datetime import datetime
from flask import Flask
from dotenv import load_dotenv

from config import Config
from extensions import db
from app_migrate import run_auto_migrations
from blueprints.admin.routes import bp as admin_bp
from blueprints.public.routes import bp as public_bp


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # --- DB 初期化 ---
    db.init_app(app)

    # --- 自動マイグレーション（SQLiteなら待ち時間ほぼゼロ）---
    with app.app_context():
        run_auto_migrations()

    # --- iframe 埋め込み許可（ブログから使う用）---
    # 例: BLOG_PARENT_ORIGINS="https://kaeruhakaeru.com/"
    origins = os.getenv("BLOG_PARENT_ORIGINS", "").strip().split()
    if origins:
        @app.after_request
        def add_embed_headers(resp):
            # 既存CSPと併用する場合はマージ処理に調整してください
            resp.headers["Content-Security-Policy"] = "frame-ancestors " + " ".join(origins)
            return resp

    # --- Blueprints ---
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # --- 初回起動：DBが空ならデモを自動投入（Shell不要対策）---
    with app.app_context():
        from models import Quiz  # 遅延 import で循環回避
        from seed import seed_demo  # 無難なデモ（カエル雑学ライト 8問）
        try:
            if Quiz.query.count() == 0:
                seed_demo()
        except Exception as e:
            # 失敗してもアプリは起動させる（ログだけ残す）
            app.logger.warning(f"[auto-seed] skipped due to error: {e}")

    # --- 便利CLI（ローカルや有料プランShell用）---
    @app.cli.command("seed_demo")
    def seed_demo_command() -> None:
        """無難なデモ診断データを投入"""
        from seed import seed_demo
        seed_demo()

    @app.cli.command("seed_sm")
    def seed_sm_command() -> None:
        """（旧）推し度診断のデモデータを投入"""
        from seed import seed_sm
        seed_sm()

    return app


app = create_app()

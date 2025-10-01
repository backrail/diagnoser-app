from __future__ import annotations

import os
import uuid
from datetime import datetime
from flask import Flask, session
from dotenv import load_dotenv

from config import Config
from extensions import db
from app_migrate import run_auto_migrations
from blueprints.admin.routes import bp as admin_bp
from blueprints.public.routes import bp as public_bp


def create_app() -> Flask:
    load_dotenv()

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )
    app.config.from_object(Config)

    # --- Jinjaで常に使える共通変数を注入 ---
    @app.context_processor
    def inject_globals():
        owner = os.getenv("SITE_OWNER", "kaeruhakaeru.com")
        year = datetime.utcnow().year
        return {
            "current_year": year,
            "site_owner": owner,
            "copyright_notice": f"© {year} {owner} All Rights Reserved.",
        }

    # --- DB 初期化 ---
    db.init_app(app)

    # --- 自動マイグレーション ---
    with app.app_context():
        run_auto_migrations()

    # --- iframe 埋め込み許可（ブログから使う用）---
    origins = os.getenv("BLOG_PARENT_ORIGINS", "").strip().split()
    if origins:
        @app.after_request
        def add_embed_headers(resp):
            resp.headers["Content-Security-Policy"] = "frame-ancestors " + " ".join(origins)
            return resp

    # --- セッションIDを必ず発行 ---
    @app.before_request
    def ensure_session_id():
        if "sid" not in session:
            session["sid"] = str(uuid.uuid4())

    # --- Blueprints 登録 ---
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # --- 初回起動時：DB初期化＋管理ユーザー作成 ---
    with app.app_context():
        try:
            from models import User
            from werkzeug.security import generate_password_hash

            db.create_all()

            admin_user = os.getenv("ADMIN_USERNAME", "admin")
            admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
            if not User.query.filter_by(username=admin_user).first():
                u = User(username=admin_user)
                if hasattr(u, "set_password"):
                    u.set_password(admin_pass)
                else:
                    u.password_hash = generate_password_hash(admin_pass)
                db.session.add(u)
                db.session.commit()
                app.logger.info(f"[auto-seed] 管理ユーザー {admin_user} を作成しました")

        except Exception as e:
            app.logger.warning(f"[auto-seed] skipped due to error: {e}")

    # --- 便利CLI ---
    @app.cli.command("seed_demo")
    def seed_demo_command() -> None:
        """無難なデモ診断データを投入"""
        from seed import seed_demo_for_session
        seed_demo_for_session("cli-demo")

    return app


app = create_app()

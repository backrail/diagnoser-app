# --- app_migrate.py: 以下の4関数をまとめて置き換え/追記してください ---
from __future__ import annotations

from extensions import db


def _has_column(table: str, column: str) -> bool:
    engine = db.engine
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table});")
        cols = [row[1] for row in rows]  # row[1] = column name
    return column in cols


def _col_meta(table: str):
    engine = db.engine
    with engine.connect() as conn:
        return list(conn.exec_driver_sql(f"PRAGMA table_info({table});"))


def _table_exists(name: str) -> bool:
    engine = db.engine
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (name,),
        )
        return bool(list(rows))


def _is_winning_trait_notnull() -> bool:
    # result.winning_trait_id が NOT NULL かどうか
    for row in _col_meta("result"):
        # row: (cid, name, type, notnull, dflt_value, pk)
        if row[1] == "winning_trait_id":
            return bool(row[3])  # 1 = NOT NULL
    return False


def run_auto_migrations() -> None:
    """SQLite向けの軽量マイグレーション（冪等）
    - choice.sum_points の追加
    - result.min_total / result.max_total の追加
    - quiz.display_mode の追加
    - quiz.choice_mode の追加  ← 追加
    - quiz.image_url の追加
    - quiz.choice_style の追加
    - question.multiple の追加
    - result.winning_trait_id の NULL 許容化
    """
    engine = db.engine
    with engine.begin() as conn:
        # --- 必要な列を追加（存在しなければ） ---
        if _table_exists("choice") and not _has_column("choice", "sum_points"):
            conn.exec_driver_sql(
                "ALTER TABLE choice ADD COLUMN sum_points INTEGER NOT NULL DEFAULT 0;"
            )

        if _table_exists("result") and not _has_column("result", "min_total"):
            conn.exec_driver_sql(
                "ALTER TABLE result ADD COLUMN min_total INTEGER NULL;"
            )
        if _table_exists("result") and not _has_column("result", "max_total"):
            conn.exec_driver_sql(
                "ALTER TABLE result ADD COLUMN max_total INTEGER NULL;"
            )

        if _table_exists("quiz") and not _has_column("quiz", "display_mode"):
            conn.exec_driver_sql(
                "ALTER TABLE quiz ADD COLUMN display_mode VARCHAR(20) NOT NULL DEFAULT 'ordered';"
            )

        # ★ 抜けていた：選択肢の並びモード
        if _table_exists("quiz") and not _has_column("quiz", "choice_mode"):
            conn.exec_driver_sql(
                "ALTER TABLE quiz ADD COLUMN choice_mode VARCHAR(20) NOT NULL DEFAULT 'ordered';"
            )

        if _table_exists("quiz") and not _has_column("quiz", "image_url"):
            conn.exec_driver_sql(
                "ALTER TABLE quiz ADD COLUMN image_url VARCHAR(500) NULL;"
            )

        if _table_exists("quiz") and not _has_column("quiz", "choice_style"):
            conn.exec_driver_sql(
                "ALTER TABLE quiz ADD COLUMN choice_style VARCHAR(20) NOT NULL DEFAULT 'normal';"
            )

        # ★ 複数選択フラグ（重複を1箇所に集約）
        if _table_exists("question") and not _has_column("question", "multiple"):
            # SQLiteのBOOLEANは整数（0/1）
            conn.exec_driver_sql(
                "ALTER TABLE question ADD COLUMN multiple INTEGER NOT NULL DEFAULT 0;"
            )

        # --- result.winning_trait_id を NULL 許容に修正（必要な場合のみ） ---
        if _table_exists("result") and _is_winning_trait_notnull():
            conn.exec_driver_sql("DROP TABLE IF EXISTS result_new;")
            conn.exec_driver_sql(
                "CREATE TABLE result_new ("
                "  id INTEGER PRIMARY KEY,"
                "  quiz_id INTEGER NOT NULL,"
                "  title VARCHAR(200) NOT NULL,"
                "  description TEXT,"
                "  min_total INTEGER NULL,"
                "  max_total INTEGER NULL,"
                "  winning_trait_id INTEGER NULL,"
                "  FOREIGN KEY(quiz_id) REFERENCES quiz (id),"
                "  FOREIGN KEY(winning_trait_id) REFERENCES trait (id)"
                ");"
            )

            cols = [c[1] for c in _col_meta("result")]
            has_min = "min_total" in cols
            has_max = "max_total" in cols
            select_min = "min_total" if has_min else "NULL"
            select_max = "max_total" if has_max else "NULL"

            conn.exec_driver_sql(
                "INSERT INTO result_new "
                "(id, quiz_id, title, description, min_total, max_total, winning_trait_id) "
                f"SELECT id, quiz_id, title, description, {select_min}, {select_max}, NULL "
                "FROM result;"
            )

            conn.exec_driver_sql("DROP TABLE result;")
            conn.exec_driver_sql("ALTER TABLE result_new RENAME TO result;")


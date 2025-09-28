from __future__ import annotations

from extensions import db
from models import Choice, Question, Quiz, Result, User


# ============================================================
# セッション単位で投入するデモ診断（カエル雑学ライト）
# ============================================================
def seed_demo_for_session(session_id: str) -> None:
    """そのセッション専用のデモ診断を投入"""
    title = f"カエル雑学ライト診断 🐸 ({session_id[:6]})"

    # 同じセッションに既にデモがあればスキップ
    old = Quiz.query.filter_by(session_id=session_id).first()
    if old:
        return

    quiz = Quiz(
        title=title,
        description="カエルに関するライトなクイズ。あなたの知識を気軽に試してみよう！",
        display_mode="ordered",
        choice_mode="ordered",
        session_id=session_id,
    )
    db.session.add(quiz)
    db.session.flush()

    order = 0

    # --- Q1 ---
    q1 = Question(
        quiz=quiz,
        text="カエルは両生類？ 爬虫類？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q1)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q1, text="両生類", sum_points=1),
            Choice(question=q1, text="爬虫類", sum_points=0),
        ]
    )

    # --- Q2 ---
    q2 = Question(
        quiz=quiz,
        text="オタマジャクシが変態すると何になる？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q2)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q2, text="カエル", sum_points=1),
            Choice(question=q2, text="ヘビ", sum_points=0),
        ]
    )

    # ===== 結果 =====
    r_good = Result(
        quiz=quiz,
        title="カエル博士！",
        description="あなたはカエルについてよく知っています。",
        min_total=2,
        max_total=9999,
    )
    r_bad = Result(
        quiz=quiz,
        title="まだまだこれから！",
        description="これからカエル知識を学んでいきましょう。",
        min_total=-9999,
        max_total=1,
    )

    db.session.add_all([r_good, r_bad])
    db.session.commit()
    print(f"[seed_demo] {title} を投入しました。")


# ============================================================
# 既存の「推し度診断」
# ============================================================
def seed_sm(db_uri_print: bool = False) -> None:
    """あなたの推したい気持ちは本物？（性欲じゃないか？）チェック"""
    if db_uri_print:
        try:
            print(f"[seed_sm] DB = {db.engine.url}")
        except Exception:
            pass

    # 管理ユーザー作成（なければ）
    if not User.query.filter_by(username="admin").first():
        from werkzeug.security import generate_password_hash

        admin = User(username="admin", password_hash=generate_password_hash("admin123"))
        db.session.add(admin)
        db.session.flush()

    title = "あなたの推したい気持ちは本物？チェック（10問）"
    old = Quiz.query.filter_by(title=title).first()
    if old:
        db.session.delete(old)
        db.session.flush()

    quiz = Quiz(
        title=title,
        description=(
            "あなたが“推している”その気持ち、本当に心からの応援かしら？\n"
            "もしかすると性欲や妄想に引っ張られているだけかも……。\n"
            "この診断で、本物度を見極めてみましょう。"
        ),
    )
    if hasattr(quiz, "display_mode"):
        quiz.display_mode = "ordered"
    db.session.add(quiz)
    db.session.flush()

    order = 0

    # （中略：Q1〜Q10の処理は現行どおり）

    # ===== 結果 =====
    r_true = Result(
        quiz=quiz,
        title="本物の推し",
        description=(
            "あなたの気持ちは純粋な応援そのもの。"
            "推しの努力や存在そのものを大切に思い、心から支えている証です。"
            "その想いはきっと推しにも届いています。"
        ),
        min_total=31,
        max_total=9999,
    )
    r_half = Result(
        quiz=quiz,
        title="曖昧（半分性欲）",
        description=(
            "あなたの推しへの想いには確かに応援の気持ちがあります。"
            "しかし同時に、欲望や妄想も混ざり込んでいるようです。"
            "応援と欲望、そのバランスをどう扱うかが課題かもしれません。"
        ),
        min_total=20,
        max_total=30,
    )
    r_false = Result(
        quiz=quiz,
        title="不純（ただの性欲）",
        description=(
            "残念ながら、あなたの推したい気持ちは純粋とは言えないようです。"
            "性的欲望が中心となっており、本来の応援とはかけ離れています。"
            "推しを尊重する気持ちを意識できれば、新しい形の推し活が見えるはず。"
        ),
        min_total=-9999,
        max_total=19,
    )

    db.session.add_all([r_true, r_half, r_false])
    db.session.commit()
    print("[seed_sm] あなたの推したい気持ちは本物？チェックを投入しました。")


# 直接実行用
if __name__ == "__main__":
    seed_sm(db_uri_print=True)

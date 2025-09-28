from __future__ import annotations

from typing import Iterable
from extensions import db
from models import Choice, Question, Quiz, Result


# ============================================================
# セッション専用：無難な8問デモ（カエル雑学ライト）
#   - そのセッションにクイズが無ければ投入（既にあれば何もしない）
#   - overwrite=True を渡すと、そのセッションの既存クイズを消してから投入
# ============================================================
def seed_demo_for_session(session_id: str, *, overwrite: bool = False) -> None:
    if not session_id:
        return

    if overwrite:
        _delete_quizzes_for_session(session_id)

    # 既存が1件でもあればスキップ（重複投入しない）
    if Quiz.query.filter_by(session_id=session_id).first():
        return

    title = "カエル雑学ライト診断"
    quiz = Quiz(
        title=title,
        description="カエルに関するやさしい8問のミニ診断です（体験用）。",
        display_mode="ordered",
        choice_mode="ordered",
        session_id=session_id,
    )
    db.session.add(quiz)
    db.session.flush()  # quiz.id を確定

    def add_q(order: int, text: str, options: Iterable[tuple[str, int]]):
        q = Question(quiz=quiz, text=text, order=order, multiple=False)
        db.session.add(q)
        db.session.flush()
        db.session.add_all([Choice(question=q, text=opt, sum_points=pt) for opt, pt in options])

    # ---- 8問（合計目安: 0〜20）----
    add_q(1, "カエルはどの分類に属する？", [("両生類", 3), ("爬虫類", 0), ("魚類", 0)])
    add_q(2, "皮膚がしっとりしている主な理由は？", [("水分保持のため", 2), ("保温のため", 1), ("体色を変えるためだけ", 0)])
    add_q(3, "多くのカエルの産卵場所は？", [("水辺", 2), ("地中深く", 0), ("木の上だけ", 1)])
    add_q(4, "春先の鳴き声の主目的は？", [("繁殖行動（なわばり・アピール）", 3), ("捕食者への威嚇", 1), ("人間への合図", 0)])
    add_q(5, "オタマジャクシから成体になる変化は？", [("変態", 3), ("変身", 1), ("脱皮", 0)])
    add_q(6, "前足と後ろ足、跳躍に強いのは？", [("後ろ足", 2), ("前足", 0), ("同じ", 1)])
    add_q(7, "夜行性が多い理由に近いのは？", [("乾燥を避けやすい", 2), ("星を見るため", 0), ("昼は眠いから", 0)])
    add_q(8, "生息に最も重要な環境要素は？", [("水と湿度", 3), ("高温", 0), ("強風", 0)])

    # ---- 結果バンド ----
    r_beginner = Result(
        quiz=quiz,
        title="入門カエラー",
        description="これからカエルの基本を知っていこう！観察のコツを学べば楽しさ倍増。",
        min_total=-9999,
        max_total=8,
    )
    r_normal = Result(
        quiz=quiz,
        title="ふつうのカエラー",
        description="身近な雑学はバッチリ。季節ごとの鳴き声や生態を調べるとさらに◎",
        min_total=9,
        max_total=15,
    )
    r_master = Result(
        quiz=quiz,
        title="上級カエラー",
        description="観察力も知識も上級。地域差や種の特徴も押さえてフィールドへ！",
        min_total=16,
        max_total=9999,
    )

    db.session.add_all([r_beginner, r_normal, r_master])
    db.session.commit()
    print(f"[seed_demo] '{title}' を session={session_id} に投入しました。")


# ============================================================
# ユーティリティ：そのセッションのクイズを全削除（体験環境のリセット用）
# ============================================================
def _delete_quizzes_for_session(session_id: str) -> int:
    if not session_id:
        return 0
    qs = Quiz.query.filter_by(session_id=session_id).all()
    deleted = 0
    for q in qs:
        db.session.delete(q)  # cascadeで子要素も削除
        deleted += 1
    if deleted:
        db.session.commit()
    return deleted

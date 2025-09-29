from __future__ import annotations

from typing import Iterable
from extensions import db
from models import Choice, Question, Quiz, Result


# ============================================================
# カエル雑学ライト診断（既存）
# ============================================================
def seed_demo_frog(session_id: str) -> None:
    if not session_id:
        return
    if Quiz.query.filter_by(session_id=session_id, title="カエル雑学ライト診断").first():
        return

    quiz = Quiz(
        title="カエル雑学ライト診断",
        description="カエルに関するやさしい8問のミニ診断です（体験用）。",
        display_mode="ordered",
        choice_mode="ordered",
        session_id=session_id,
    )
    db.session.add(quiz)
    db.session.flush()

    def add_q(order: int, text: str, options: Iterable[tuple[str, int]]):
        q = Question(quiz=quiz, text=text, order=order, multiple=False)
        db.session.add(q)
        db.session.flush()
        db.session.add_all([Choice(question=q, text=opt, sum_points=pt) for opt, pt in options])

    add_q(1, "カエルはどの分類に属する？", [("両生類", 3), ("爬虫類", 0), ("魚類", 0)])
    add_q(2, "皮膚がしっとりしている主な理由は？", [("水分保持のため", 2), ("保温のため", 1), ("体色を変えるためだけ", 0)])
    add_q(3, "多くのカエルの産卵場所は？", [("水辺", 2), ("地中深く", 0), ("木の上だけ", 1)])
    add_q(4, "春先の鳴き声の主目的は？", [("繁殖行動", 3), ("捕食者への威嚇", 1), ("人間への合図", 0)])
    add_q(5, "オタマジャクシから成体になる変化は？", [("変態", 3), ("変身", 1), ("脱皮", 0)])
    add_q(6, "前足と後ろ足、跳躍に強いのは？", [("後ろ足", 2), ("前足", 0), ("同じ", 1)])
    add_q(7, "夜行性が多い理由に近いのは？", [("乾燥を避けやすい", 2), ("星を見るため", 0), ("昼は眠いから", 0)])
    add_q(8, "生息に最も重要な環境要素は？", [("水と湿度", 3), ("高温", 0), ("強風", 0)])

    db.session.add_all([
        Result(quiz=quiz, title="入門カエラー", description="これからカエルの基本を知っていこう！", min_total=-9999, max_total=8),
        Result(quiz=quiz, title="ふつうのカエラー", description="身近な雑学はバッチリ。さらに知識を深めよう！", min_total=9, max_total=15),
        Result(quiz=quiz, title="上級カエラー", description="観察力も知識も上級。フィールドへ！", min_total=16, max_total=9999),
    ])
    db.session.commit()
    print(f"[seed_demo_frog] カエル診断を session={session_id} に投入")


# ============================================================
# 新規：シンプル性格診断（10問）
# ============================================================
def seed_demo_personality(session_id: str) -> None:
    if not session_id:
        return
    if Quiz.query.filter_by(session_id=session_id, title="シンプル性格診断").first():
        return

    quiz = Quiz(
        title="シンプル性格診断",
        description="あなたの性格タイプを10問でざっくり診断します。",
        display_mode="ordered",
        choice_mode="ordered",
        session_id=session_id,
    )
    db.session.add(quiz)
    db.session.flush()

    def add_q(order: int, text: str):
        q = Question(quiz=quiz, text=text, order=order, multiple=False)
        db.session.add(q)
        db.session.flush()
        db.session.add_all([
            Choice(question=q, text="はい", sum_points=2),
            Choice(question=q, text="どちらともいえない", sum_points=1),
            Choice(question=q, text="いいえ", sum_points=0),
        ])

    questions = [
        "人と一緒に過ごすのが好きだ",
        "初対面の人ともすぐ打ち解けられる",
        "計画を立てて行動する方だ",
        "思いつきで行動することが多い",
        "一人の時間が必要だと感じる",
        "人に相談するより自分で解決したい",
        "細かいところが気になる",
        "大雑把でも気にしない",
        "感情表現は豊かな方だ",
        "どちらかというと冷静な方だ",
    ]

    for idx, text in enumerate(questions, start=1):
        add_q(idx, text)

    db.session.add_all([
        Result(
            quiz=quiz,
            title="外交的タイプ",
            description="社交的でエネルギッシュ。人との交流から力を得ます。",
            min_total=16,
            max_total=20,
        ),
        Result(
            quiz=quiz,
            title="バランスタイプ",
            description="状況に応じて柔軟にふるまえる中庸タイプです。",
            min_total=8,
            max_total=15,
        ),
        Result(
            quiz=quiz,
            title="内向的タイプ",
            description="落ち着きがあり、一人で考えることを大切にします。",
            min_total=-9999,
            max_total=7,
        ),
    ])
    db.session.commit()
    print(f"[seed_demo_personality] 性格診断を session={session_id} に投入")


# ============================================================
# エントリーポイント：両方投入
# ============================================================
def seed_demo_for_session(session_id: str) -> None:
    seed_demo_frog(session_id)
    seed_demo_personality(session_id)

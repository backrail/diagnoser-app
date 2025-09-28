from __future__ import annotations

from extensions import db
from models import Choice, Question, Quiz, Result, User


# ============================================================
# あなたの推したい気持ちは本物？チェック（10問）
#   - 性欲寄りかどうかを判定
#   - 結果は「本物の推し／曖昧／不純」
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

    # --- Q1 ---
    q = Question(
        quiz=quiz,
        text="推しのどんな瞬間を一番強く思い出す？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="パフォーマンス中の真剣な表情", sum_points=4),
            Choice(question=q, text="バラエティや配信での素の笑顔", sum_points=3),
            Choice(question=q, text="衣装や肌の露出が多い場面", sum_points=1),
        ]
    )

    # --- Q2 ---
    q = Question(
        quiz=quiz,
        text="推しのグッズを買うとき、何を想像する？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="部屋に飾って眺めて元気をもらう", sum_points=4),
            Choice(question=q, text="現地で使って一体感を楽しむ", sum_points=3),
            Choice(question=q, text="妄想に使うために買う", sum_points=1),
        ]
    )

    # --- Q3 ---
    q = Question(
        quiz=quiz,
        text="推しのSNS投稿、どんな内容が嬉しい？（複数可）",
        order=order,
        multiple=True,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="活動報告や告知で頑張りが伝わる", sum_points=3),
            Choice(question=q, text="素朴な日常のつぶやき", sum_points=2),
            Choice(question=q, text="ちょっとセクシーな写真", sum_points=1),
        ]
    )

    # --- Q4 ---
    q = Question(
        quiz=quiz,
        text="ライブに行ったとき、どんな感情が強い？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="一緒に夢を追っているような感動", sum_points=4),
            Choice(question=q, text="推しが楽しんでる姿を見て安心", sum_points=3),
            Choice(question=q, text="近くで見たい、触れたいという衝動", sum_points=1),
        ]
    )

    # --- Q5 ---
    q = Question(
        quiz=quiz,
        text="推しのビジュアルで一番惹かれるところは？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="努力がにじむ目や表情", sum_points=4),
            Choice(question=q, text="髪型やファッションセンス", sum_points=3),
            Choice(question=q, text="体のラインや露出部分", sum_points=1),
        ]
    )

    # --- Q6 ---
    q = Question(
        quiz=quiz,
        text="ファン同士での交流で大事にしていることは？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="推しの魅力や努力を共有して高め合う", sum_points=4),
            Choice(question=q, text="イベントの感想を語り合う", sum_points=3),
            Choice(question=q, text="推しの性的な妄想をネタに盛り上がる", sum_points=1),
        ]
    )

    # --- Q7 ---
    q = Question(
        quiz=quiz,
        text="推しのためにお金や時間を使うときの気持ちは？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="推しの活動が続くための投資と思う", sum_points=4),
            Choice(question=q, text="自分の楽しみとして惜しみなく出す", sum_points=3),
            Choice(question=q, text="推し本人と繋がる妄想に浸りながら出す", sum_points=1),
        ]
    )

    # --- Q8 ---
    q = Question(
        quiz=quiz,
        text="もし推しが恋愛したと知ったら？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="幸せなら応援できる", sum_points=4),
            Choice(question=q, text="正直ショックだが活動を応援する", sum_points=3),
            Choice(question=q, text="独占欲と嫉妬で苦しくなる", sum_points=1),
        ]
    )

    # --- Q9 ---
    q = Question(
        quiz=quiz,
        text="推しを夢に見たときの感覚は？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="隣で笑ってくれる夢なら幸せ", sum_points=4),
            Choice(question=q, text="一緒に遊んでる夢で元気が出る", sum_points=3),
            Choice(question=q, text="肌を重ねる夢で興奮してしまう", sum_points=1),
        ]
    )

    # --- Q10 ---
    q = Question(
        quiz=quiz,
        text="推しの存在をどう言い表す？",
        order=order,
        multiple=False,
    )
    order += 1
    db.session.add(q)
    db.session.flush()
    db.session.add_all(
        [
            Choice(question=q, text="人生を照らす光", sum_points=4),
            Choice(question=q, text="毎日の活力", sum_points=3),
            Choice(question=q, text="性的欲望の対象", sum_points=1),
        ]
    )

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


# ============================================================
# カエル雑学ライト診断（8問）— 無難なデモ
#   - 合計点で「入門／ふつう／上級」を判定
# ============================================================
def seed_demo(db_uri_print: bool = False) -> None:
    if db_uri_print:
        try:
            print(f"[seed_demo] DB = {db.engine.url}")
        except Exception:
            pass

    from models import Quiz, Question, Choice, Result
    title = "カエル雑学ライト診断"
    Quiz.query.filter_by(title=title).delete()

    quiz = Quiz(
        title=title,
        description="カエルに関するやさしい雑学の8問ミニ診断です。軽いデモ用コンテンツ。",
    )
    db.session.add(quiz)
    db.session.flush()

    order = 1
    def add_q(text, opts):
        nonlocal order
        q = Question(quiz=quiz, text=text, order=order, multiple=False)
        order += 1
        db.session.add(q)
        db.session.flush()
        db.session.add_all([Choice(question=q, text=o[0], sum_points=o[1]) for o in opts])

    add_q("日本に生息するカエルの一般的な分類で正しいのは？",
          [("両生類", 3), ("爬虫類", 0), ("魚類", 0)])
    add_q("カエルの皮膚がしっとりしている主な理由は？",
          [("水分保持のため", 2), ("保温のため", 1), ("体色を変えるためだけ", 0)])
    add_q("多くのカエルの産卵場所は？",
          [("水辺", 2), ("地中深く", 0), ("木の上だけ", 1)])
    add_q("春先によく聞くカエルの鳴き声は主に何のため？",
          [("繁殖行動（なわばり・アピール）", 3), ("捕食者への威嚇", 1), ("人間への合図", 0)])
    add_q("オタマジャクシから成体になる変化を何という？",
          [("変態", 3), ("変身", 1), ("脱皮", 0)])
    add_q("カエルの前足と後ろ足で一般に強いのは？",
          [("後ろ足（跳躍に特化）", 2), ("前足", 0), ("同じ", 1)])
    add_q("夜に活動する種類が多い理由として近いのは？",
          [("乾燥を避けやすい", 2), ("星を観察するため", 0), ("昼は眠いから", 0)])
    add_q("カエルの生息にとって最も重要な環境要素は？",
          [("水と湿度", 3), ("高温", 0), ("強風", 0)])

    r_beginner = Result(quiz=quiz, title="入門カエラー",
        description="これからカエルの世界へようこそ。基本をおさえれば、もっと観察が楽しくなります。",
        min_total=-9999, max_total=8)
    r_normal = Result(quiz=quiz, title="ふつうのカエラー",
        description="身近な雑学はバッチリ。季節ごとの鳴き声や生態を調べると、さらに理解が深まります。",
        min_total=9, max_total=15)
    r_master = Result(quiz=quiz, title="上級カエラー",
        description="観察力も知識も上級者。地域差や種ごとの特徴も押さえて、フィールドに出れば発見だらけ。",
        min_total=16, max_total=9999)

    db.session.add_all([r_beginner, r_normal, r_master])
    db.session.commit()
    print("[seed_demo] カエル雑学ライト診断を投入しました。")

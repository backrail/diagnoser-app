from __future__ import annotations
import random
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort
from models import Quiz, sum_total, pick_result_by_total

bp = Blueprint("public", __name__)

# ---- セッションID（ログイン不要デモ用） ----
def current_sid() -> str:
    sid = session.get("sid")
    if not sid:
        sid = session["sid"] = uuid.uuid4().hex  # 念のため保険（app.before_request でも付与）
    return sid

# ---- ヘルスチェック（デプロイ確認用）----
@bp.get("/healthz")
def healthz():
    return {"status": "ok"}

# ---- トップ：自分のセッションの診断だけ表示。無ければ自動デモ投入 ----
@bp.get("/")
def index():
    sid = current_sid()
    quizzes = Quiz.query.filter_by(session_id=sid).order_by(Quiz.id.asc()).all()
    if not quizzes:
        try:
            # そのセッション専用のデモを1回だけ投入
            from seed import seed_demo_for_session
            seed_demo_for_session(sid)
            quizzes = Quiz.query.filter_by(session_id=sid).order_by(Quiz.id.asc()).all()
        except Exception:
            # 失敗しても表示は続行（空一覧）
            pass
    return render_template("public/index.html", quizzes=quizzes)

# ---- 受験開始：他人のセッションのデータは見えない ----
@bp.get("/quiz/<int:quiz_id>")
def quiz_start(quiz_id: int):
    sid = current_sid()
    quiz = Quiz.query.filter_by(id=quiz_id, session_id=sid).first()
    if not quiz:
        abort(404)

    # --- 質問の並び ---
    if getattr(quiz, "display_mode", "ordered") == "random":
        questions = list(quiz.questions)
        random.shuffle(questions)
    else:
        questions = sorted(quiz.questions, key=lambda q: (q.order or 0, q.id))

    # --- 選択肢の並び ---
    choice_mode = getattr(quiz, "choice_mode", "ordered")
    for q in questions:
        if choice_mode == "random":
            shuffled = list(q.choices)
            random.shuffle(shuffled)
            q._shuffled_choices = shuffled        # テンプレが使う一時属性
        else:
            q._shuffled_choices = sorted(q.choices, key=lambda c: c.id)

    return render_template("public/quiz_form.html", quiz=quiz, questions=questions)

# ---- 結果判定：同じく自分のセッションのクイズに限定 ----
@bp.post("/quiz/<int:quiz_id>/result")
def quiz_result(quiz_id: int):
    sid = current_sid()
    quiz = Quiz.query.filter_by(id=quiz_id, session_id=sid).first()
    if not quiz:
        abort(404)

    picked: list[int] = []
    for q in quiz.questions:
        field = f"q-{q.id}"
        if getattr(q, "multiple", False):
            # 複数選択：同名フィールドをすべて取得
            for v in request.form.getlist(field):
                try:
                    picked.append(int(v))
                except (TypeError, ValueError):
                    pass
        else:
            # 単一選択
            v = request.form.get(field)
            if v:
                try:
                    picked.append(int(v))
                except (TypeError, ValueError):
                    pass

    total = sum_total(picked)
    result = pick_result_by_total(quiz, total)
    if not result:
        flash("結果を判定できませんでした。レンジ設定を見直してください。", "warning")
        return redirect(url_for("public.quiz_start", quiz_id=quiz.id))

    return render_template("public/result.html", quiz=quiz, result=result, total=total)

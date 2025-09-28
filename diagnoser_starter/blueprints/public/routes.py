from __future__ import annotations
import random
from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import Quiz, sum_total, pick_result_by_total

bp = Blueprint("public", __name__)

@bp.get("/")
def index():
    quizzes = Quiz.query.all()
    return render_template("public/index.html", quizzes=quizzes)

@bp.get("/quiz/<int:quiz_id>")
def quiz_start(quiz_id: int):
    quiz = Quiz.query.get_or_404(quiz_id)

    # --- 質問の並び ---
    if getattr(quiz, "display_mode", "ordered") == "random":
        questions = list(quiz.questions)
        random.shuffle(questions)
    else:
        questions = sorted(quiz.questions, key=lambda q: (q.order or 0, q.id))

    # --- 選択肢の並び（★追加） ---
    choice_mode = getattr(quiz, "choice_mode", "ordered")
    for q in questions:
        if choice_mode == "random":
            shuffled = list(q.choices)
            random.shuffle(shuffled)
            q._shuffled_choices = shuffled        # ← テンプレが使う一時属性
        else:
            # “管理順どおり”を安定させたいので id で固定（必要なら別キーに変更）
            q._shuffled_choices = sorted(q.choices, key=lambda c: c.id)

    return render_template("public/quiz_form.html", quiz=quiz, questions=questions)

@bp.post("/quiz/<int:quiz_id>/result")
def quiz_result(quiz_id: int):
    quiz = Quiz.query.get_or_404(quiz_id)
    picked: list[int] = []

    # publicテンプレートでは questions を渡していても、ここでは quiz.questions を基準に集計してOK
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
            # 単一選択：1件だけ
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

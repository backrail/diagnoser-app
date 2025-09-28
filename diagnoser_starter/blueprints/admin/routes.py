from __future__ import annotations

import os
import time
import uuid
from functools import wraps
from typing import Callable

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort,
)
from werkzeug.utils import secure_filename

from extensions import db
from models import Choice, Question, Quiz, Result, Trait, User

bp = Blueprint("admin", __name__, url_prefix="/admin")


# ------------ 共通ユーティリティ ------------

def current_sid() -> str:
    """Flask セッションに付与された一意ID（app.py の before_request で発行）"""
    sid = session.get("sid")
    if not sid:
        # 念のため保険（通常は app.before_request で必ず入る）
        sid = session["sid"] = uuid.uuid4().hex
    return sid


# ------------ 認証ユーティリティ（既存のまま） ------------

def is_logged_in() -> bool:
    return bool(session.get("admin_user_id"))


def login_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("admin.login"))
        return func(*args, **kwargs)
    return wrapper


# ------------ アップロードユーティリティ ------------

def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get(
        "ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"}
    )
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _save_upload(file_storage) -> str | None:
    if not file_storage or not file_storage.filename:
        return None
    if not _allowed_file(file_storage.filename):
        return None

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    base = secure_filename(file_storage.filename)
    name, ext = os.path.splitext(base)
    unique = f"{name}_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
    abs_path = os.path.join(upload_dir, unique)
    file_storage.save(abs_path)

    return f"/{abs_path.replace(os.sep, '/')}"


# ------------ 認証 ------------

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["admin_user_id"] = user.id
            return redirect(url_for("admin.dashboard"))
        flash("ユーザー名またはパスワードが違います。", "danger")
    return render_template("admin/login.html")


@bp.get("/logout")
def logout():
    # セッションのログイン情報のみ消す（sid は残す）
    session.pop("admin_user_id", None)
    return redirect(url_for("admin.login"))


# ------------ ダッシュボード（セッションで分離） ------------

@bp.get("/")
@login_required
def dashboard():
    sid = current_sid()
    quizzes = Quiz.query.filter_by(session_id=sid).order_by(Quiz.id.asc()).all()
    return render_template("admin/dashboard.html", quizzes=quizzes)


@bp.get("/", endpoint="index")
@login_required
def admin_index():
    sid = current_sid()
    quizzes = Quiz.query.filter_by(session_id=sid).order_by(Quiz.id.asc()).all()
    return render_template("admin/dashboard.html", quizzes=quizzes)


# ------------ 診断 CRUD（セッションで分離） ------------

@bp.route("/quiz/new", methods=["GET", "POST"])
@login_required
def quiz_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        desc = request.form.get("description", "").strip()
        if not title:
            flash("タイトルは必須です。", "warning")
        else:
            qz = Quiz(title=title, description=desc, session_id=current_sid())
            db.session.add(qz)
            db.session.commit()
            return redirect(url_for("admin.quiz_edit", quiz_id=qz.id))
    return render_template("admin/quiz_edit.html", quiz=None)


def _get_own_quiz_or_404(quiz_id: int) -> Quiz:
    """現在セッションの所有 Quiz を取得（他人のは 404）"""
    sid = current_sid()
    qz = Quiz.query.filter_by(id=quiz_id, session_id=sid).first()
    if not qz:
        abort(404)
    return qz


@bp.post("/quiz/<int:quiz_id>/delete")
@login_required
def quiz_delete(quiz_id: int):
    quiz = _get_own_quiz_or_404(quiz_id)
    title = quiz.title
    db.session.delete(quiz)  # 子は cascade で削除
    db.session.commit()
    flash(f"『{title}』を削除しました。", "success")
    return redirect(url_for("admin.index"))


@bp.route("/quiz/<int:quiz_id>/edit", methods=["GET", "POST"])
@login_required
def quiz_edit(quiz_id: int):
    """※ この関数は1つだけにする（重複定義禁止）"""
    quiz = _get_own_quiz_or_404(quiz_id)

    if request.method == "POST":
        # 基本情報
        quiz.title = (request.form.get("title") or quiz.title).strip()
        quiz.description = (request.form.get("description") or quiz.description).strip()

        # 質問の表示順
        display_mode = request.form.get("display_mode", "ordered")
        quiz.display_mode = (
            display_mode if display_mode in ("ordered", "random") else "ordered"
        )

        # 選択肢の表示順
        choice_mode = request.form.get("choice_mode", "ordered")
        quiz.choice_mode = (
            choice_mode if choice_mode in ("ordered", "random") else "ordered"
        )

        # ラジオボタンのデザイン
        choice_style = request.form.get("choice_style", "normal")
        quiz.choice_style = (
            choice_style
            if choice_style in ("normal", "heart", "star", "diamond")
            else "normal"
        )

        # 画像アップロード（任意）
        file = request.files.get("image_file")
        if file and file.filename:
            url = _save_upload(file)
            if url:
                quiz.image_url = url
            else:
                flash("画像のアップロードに失敗しました（拡張子など）", "warning")

        # 画像削除
        if request.form.get("remove_image") == "1":
            quiz.image_url = None

        db.session.commit()
        flash("保存しました。", "success")
        return redirect(url_for("admin.quiz_edit", quiz_id=quiz.id))

    return render_template("admin/quiz_edit.html", quiz=quiz)


# ------------ 質問・選択肢（セッションで分離） ------------

def _ensure_question_belongs_to_me(q: Question) -> None:
    if not q or not q.quiz or q.quiz.session_id != current_sid():
        abort(404)


@bp.route("/quiz/<int:quiz_id>/questions", methods=["GET", "POST"])
@login_required
def questions(quiz_id: int):
    quiz = _get_own_quiz_or_404(quiz_id)
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            current = sorted(quiz.questions, key=lambda x: (x.order or 0, x.id))
            max_order = current[-1].order if current else -1
            q = Question(quiz=quiz, text=text, order=(max_order or 0) + 1)
            db.session.add(q)
            db.session.commit()
            flash("質問を追加しました（末尾）。", "success")
        else:
            flash("質問文は必須です。", "warning")
    return render_template("admin/questions.html", quiz=quiz)


@bp.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def question_edit(question_id: int):
    q = Question.query.get_or_404(question_id)
    _ensure_question_belongs_to_me(q)
    if request.method == "POST":
        q.text = request.form.get("text", q.text).strip()
        q.multiple = request.form.get("multiple") == "1"
        db.session.commit()
        flash("保存しました。", "success")
    return render_template("admin/question_form.html", q=q)


@bp.post("/question/<int:question_id>/delete")
@login_required
def question_delete(question_id: int):
    q = Question.query.get_or_404(question_id)
    _ensure_question_belongs_to_me(q)
    quiz_id = q.quiz_id
    db.session.delete(q)
    db.session.commit()
    flash("削除しました。", "success")
    return redirect(url_for("admin.questions", quiz_id=quiz_id))


@bp.post("/question/<int:question_id>/move/<string:direction>")
@login_required
def question_move(question_id: int, direction: str):
    q = Question.query.get_or_404(question_id)
    _ensure_question_belongs_to_me(q)
    quiz = q.quiz
    qs = sorted(quiz.questions, key=lambda x: (x.order or 0, x.id))
    for idx, item in enumerate(qs):
        item.order = idx
    db.session.flush()

    qs = sorted(quiz.questions, key=lambda x: x.order or 0)
    idx = next((i for i, iq in enumerate(qs) if iq.id == q.id), None)
    if idx is None:
        flash("順番の取得に失敗しました。", "warning")
        return redirect(url_for("admin.questions", quiz_id=quiz.id))
    if direction == "up" and idx > 0:
        qs[idx].order, qs[idx - 1].order = qs[idx - 1].order, qs[idx].order
    elif direction == "down" and idx < len(qs) - 1:
        qs[idx].order, qs[idx + 1].order = qs[idx + 1].order, qs[idx].order

    db.session.commit()
    return redirect(url_for("admin.questions", quiz_id=quiz.id))


@bp.post("/question/<int:question_id>/choice/new")
@login_required
def choice_new(question_id: int):
    q = Question.query.get_or_404(question_id)
    _ensure_question_belongs_to_me(q)
    text = request.form.get("text", "").strip()
    if text:
        ch = Choice(question=q, text=text)
        try:
            ch.sum_points = int(request.form.get("sum_points") or 0)
        except ValueError:
            ch.sum_points = 0
        db.session.add(ch)
        db.session.commit()
        flash("選択肢を追加しました。", "success")
    else:
        flash("選択肢の文言は必須です。", "warning")
    return redirect(url_for("admin.question_edit", question_id=question_id))


@bp.post("/choice/<int:choice_id>/delete")
@login_required
def choice_delete(choice_id: int):
    ch = Choice.query.get_or_404(choice_id)
    # 親質問の所有確認
    _ensure_question_belongs_to_me(ch.question)
    qid = ch.question_id
    db.session.delete(ch)
    db.session.commit()
    flash("削除しました。", "success")
    return redirect(url_for("admin.question_edit", question_id=qid))


@bp.post("/choice/<int:choice_id>/score")
@login_required
def choice_score_update(choice_id: int):
    ch = Choice.query.get_or_404(choice_id)
    _ensure_question_belongs_to_me(ch.question)

    new_text = request.form.get("text")
    if new_text is not None and new_text.strip():
        ch.text = new_text.strip()
    try:
        ch.sum_points = int(request.form.get("sum_points") or 0)
    except ValueError:
        ch.sum_points = 0
    db.session.commit()
    flash("選択肢を保存しました。", "success")
    return redirect(url_for("admin.question_edit", question_id=ch.question_id))


# ------------ 結果（セッションで分離） ------------

def _ensure_result_belongs_to_me(r: Result) -> None:
    if not r or not r.quiz or r.quiz.session_id != current_sid():
        abort(404)


@bp.route("/quiz/<int:quiz_id>/results", methods=["GET", "POST"])
@login_required
def results(quiz_id: int):
    quiz = _get_own_quiz_or_404(quiz_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        try:
            min_total = (
                int(request.form.get("min_total"))
                if request.form.get("min_total") not in (None, "")
                else None
            )
        except ValueError:
            min_total = None
        try:
            max_total = (
                int(request.form.get("max_total"))
                if request.form.get("max_total") not in (None, "")
                else None
            )
        except ValueError:
            max_total = None

        if not title:
            flash("タイトルは必須です。", "warning")
        else:
            r = Result(
                quiz=quiz,
                title=title,
                description=description,
                min_total=min_total,
                max_total=max_total,
            )
            db.session.add(r)
            db.session.commit()
            flash("結果を追加しました。", "success")
    return render_template("admin/results.html", quiz=quiz)


@bp.post("/result/<int:result_id>/delete")
@login_required
def result_delete(result_id: int):
    r = Result.query.get_or_404(result_id)
    _ensure_result_belongs_to_me(r)
    qid = r.quiz_id
    db.session.delete(r)
    db.session.commit()
    flash("削除しました。", "success")
    return redirect(url_for("admin.results", quiz_id=qid))


@bp.post("/result/<int:result_id>/update")
@login_required
def result_update(result_id: int):
    r = Result.query.get_or_404(result_id)
    _ensure_result_belongs_to_me(r)

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()

    min_raw = request.form.get("min_total", "").strip()
    max_raw = request.form.get("max_total", "").strip()
    try:
        min_total = int(min_raw) if min_raw != "" else None
    except ValueError:
        min_total = None
    try:
        max_total = int(max_raw) if max_raw != "" else None
    except ValueError:
        max_total = None

    if not title:
        flash("タイトルは必須です。", "warning")
        return redirect(url_for("admin.results", quiz_id=r.quiz_id))

    r.title = title
    r.description = description
    r.min_total = min_total
    r.max_total = max_total

    db.session.commit()
    flash("結果を更新しました。", "success")
    return redirect(url_for("admin.results", quiz_id=r.quiz_id))

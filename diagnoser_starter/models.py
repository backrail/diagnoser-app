from __future__ import annotations
from typing import List
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- Admin User ----------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

# ---------- Quiz Domain ----------
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    display_mode = db.Column(db.String(20), nullable=False, default="ordered")
    choice_mode = db.Column(db.String(20), nullable=False, default="ordered")

    image_url = db.Column(db.String(500), nullable=True)

    choice_style = db.Column(db.String(20), nullable=False, default="normal")

    traits = db.relationship("Trait", backref="quiz", cascade="all, delete-orphan")
    questions = db.relationship("Question", backref="quiz", cascade="all, delete-orphan")
    results = db.relationship("Result", backref="quiz", cascade="all, delete-orphan")


class Trait(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    key = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)
    multiple = db.Column(db.Boolean, nullable=False, default=False)

    choices = db.relationship(
        "Choice",
        backref="question",
        cascade="all, delete-orphan",
    )


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    sum_points = db.Column(db.Integer, default=0, nullable=False)

    scores = db.relationship("ChoiceScore", backref="choice", cascade="all, delete-orphan")

class ChoiceScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"), nullable=False)
    trait_id = db.Column(db.Integer, db.ForeignKey("trait.id"), nullable=False)
    points = db.Column(db.Integer, default=0)

    trait = db.relationship("Trait")

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    min_total = db.Column(db.Integer, nullable=True)
    max_total = db.Column(db.Integer, nullable=True)
    winning_trait_id = db.Column(db.Integer, db.ForeignKey("trait.id"), nullable=True)
    winning_trait = db.relationship("Trait")

# ---------- Sum Scoring Helpers (restored) ----------

def sum_total(picked_choice_ids: List[int]) -> int:
    """Return single total by summing Choice.sum_points for given choice IDs."""
    if not picked_choice_ids:
        return 0
    rows = Choice.query.filter(Choice.id.in_(picked_choice_ids)).all()
    return sum(int(getattr(ch, "sum_points", 0) or 0) for ch in rows)

def pick_result_by_total(quiz: Quiz, total: int) -> Result | None:
    """Pick first Result whose [min_total, max_total] band contains total."""
    for r in quiz.results:
        lo = r.min_total if r.min_total is not None else -10**9
        hi = r.max_total if r.max_total is not None else  10**9
        if lo <= total <= hi:
            return r
    return None

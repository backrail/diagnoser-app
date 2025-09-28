from __future__ import annotations
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///diagnoser.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

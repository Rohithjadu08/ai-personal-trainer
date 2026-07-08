from typing import Any, Dict, Optional
from dataclasses import dataclass
import time
import os

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .auth import get_password_hash


@dataclass
class User:
    id: str
    email: str
    name: str
    password_hash: str


Base = declarative_base()


class UserRow(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(Text, nullable=False)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
_engine = None
_SessionLocal = None


def _ensure_engine():
    global _engine, _SessionLocal
    if _engine is None:
        connect_args = {}
        if DATABASE_URL.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
        Base.metadata.create_all(_engine)
        _SessionLocal = sessionmaker(bind=_engine, future=True)
    return _SessionLocal


class Database:
    """Persistent SQLite-backed store (auth-critical). Plans/chats are kept for
    API compatibility; extend here if you need to persist them later."""

    def _new_session(self) -> Session:
        SessionLocal = _ensure_engine()
        return SessionLocal()

    def _gen_id(self) -> str:
        import uuid

        return str(uuid.uuid4())

    def get_user_by_email(self, email: str) -> Optional[User]:
        session = self._new_session()
        try:
            row = session.query(UserRow).filter(UserRow.email == email).first()
            if not row:
                return None
            return User(
                id=row.id, email=row.email, name=row.name, password_hash=row.password_hash
            )
        finally:
            session.close()

    def create_user(self, email: str, password: str, name: str) -> User:
        session = self._new_session()
        try:
            user = UserRow(
                id=self._gen_id(),
                email=email,
                name=name,
                password_hash=get_password_hash(password),
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return User(
                id=user.id,
                email=user.email,
                name=user.name,
                password_hash=user.password_hash,
            )
        finally:
            session.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        session = self._new_session()
        try:
            row = session.get(UserRow, str(user_id))
            if not row:
                return None
            return User(
                id=row.id, email=row.email, name=row.name, password_hash=row.password_hash
            )
        finally:
            session.close()

    def get_user_profile_stats(self, user_id: str) -> dict:
        return {"last_login": int(time.time()), "workouts_completed": 0}

    def save_plan(self, user_id: str, plan_type: str, plan: Any) -> None:
        # Kept for API compatibility; persists nothing in the minimal store.
        return None

    def save_chat_message(
        self, user_id: str, message: str, reply: str, source: str
    ) -> None:
        # Kept for API compatibility; persists nothing in the minimal store.
        return None


# Module-level singleton for the DB engine across requests.
_DB_INSTANCE: Optional[Database] = None


def get_db() -> Database:
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = Database()
    return _DB_INSTANCE

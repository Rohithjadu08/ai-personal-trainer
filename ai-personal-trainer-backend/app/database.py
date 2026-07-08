from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class User:
	id: str
	email: str
	name: str
	password_hash: str


class Database:
	def __init__(self):
		# simple in-memory stores
		self._users: Dict[str, User] = {}
		self._by_email: Dict[str, User] = {}
		self._plans: Dict[str, Any] = {}
		self._chats: Dict[str, list] = {}
		self._next_id = 1

	def _gen_id(self) -> str:
		nid = str(self._next_id)
		self._next_id += 1
		return nid

	def get_user_by_email(self, email: str) -> Optional[User]:
		return self._by_email.get(email)

	def create_user(self, email: str, password: str, name: str) -> User:
		# store hashed password expected by auth.verify_password
		from .auth import get_password_hash

		uid = self._gen_id()
		ph = get_password_hash(password)
		user = User(id=uid, email=email, name=name, password_hash=ph)
		self._users[uid] = user
		self._by_email[email] = user
		return user

	def get_user_by_id(self, user_id: str) -> Optional[User]:
		return self._users.get(str(user_id))

	def get_user_profile_stats(self, user_id: str) -> dict:
		# stubbed profile stats
		return {"last_login": int(time.time()), "workouts_completed": 0}

	def save_plan(self, user_id: str, plan_type: str, plan: Any) -> None:
		self._plans.setdefault(user_id, {})[plan_type] = plan

	def save_chat_message(self, user_id: str, message: str, reply: str, source: str) -> None:
		self._chats.setdefault(user_id, []).append({"message": message, "reply": reply, "source": source})


# Module-level singleton for simple in-memory DB across requests
_DB_INSTANCE: Optional[Database] = None


def get_db() -> Database:
	global _DB_INSTANCE
	if _DB_INSTANCE is None:
		_DB_INSTANCE = Database()
	return _DB_INSTANCE



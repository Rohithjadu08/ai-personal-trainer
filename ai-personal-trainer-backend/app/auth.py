from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
	try:
		return pwd_context.verify(plain, hashed)
	except Exception:
		return False


def create_access_token(subject: str, expires_delta: Optional[timedelta], secret: str, algorithm: str) -> str:
	to_encode = {"sub": str(subject)}
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
		to_encode.update({"exp": expire})
	return jwt.encode(to_encode, secret, algorithm=algorithm)



# auth.py
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from .utils import DatabasePool

router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))


class User(BaseModel):
    username: str
    password: str


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token


# REGISTER
@router.post("/register")
def register(user: User):
    try:
        conn = DatabasePool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=%s", (user.username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="User already exists ❌")
            password_hash = _hash_password(user.password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (user.username, password_hash)
            )
            conn.commit()
            return {"status": "success", "message": "Registration successful ✅"}
        finally:
            cursor.close()
            conn.close()
    except Exception:
        # Fallback to in-memory for dev if DB unavailable
        global _memory_users
        try:
            _memory_users
        except NameError:
            _memory_users = {}
        if user.username in _memory_users:
            raise HTTPException(status_code=400, detail="User already exists ❌")
        _memory_users[user.username] = _hash_password(user.password)
        return {"status": "success", "message": "Registration successful ✅ (memory)"}


# LOGIN
@router.post("/login")
def login(user: User):
    try:
        conn = DatabasePool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash FROM users WHERE username=%s", (user.username,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="User not found ❌")
            user_id, password_hash = row
            if not _verify_password(user.password, password_hash):
                raise HTTPException(status_code=401, detail="Incorrect password ❌")
            token = _create_access_token(user.username)
            return {"status": "success", "message": f"Welcome {user.username} 🌱", "token": token}
        finally:
            cursor.close()
            conn.close()
    except Exception:
        # Fallback to in-memory for dev if DB unavailable
        global _memory_users
        try:
            stored_hash = _memory_users.get(user.username)
        except NameError:
            stored_hash = None
        if not stored_hash:
            raise HTTPException(status_code=401, detail="User not found ❌")
        if not _verify_password(user.password, stored_hash):
            raise HTTPException(status_code=401, detail="Incorrect password ❌")
        token = _create_access_token(user.username)
        return {"status": "success", "message": f"Welcome {user.username} 🌱 (memory)", "token": token}

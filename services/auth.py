# auth.py
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from .utils import DatabasePool

router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))
AUTH_COOKIE_NAME = "krishi_token"


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


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# REGISTER
@router.post("/register")
def register(user: User):
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


# LOGIN
@router.post("/login")
def login(user: User, response: Response):
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
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return {"status": "success", "message": f"Welcome {user.username} 🌱"}
    finally:
        cursor.close()
        conn.close()


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    return {"status": "success", "message": "Logged out"}


@router.get("/whoami")
def whoami(request: Request):
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    username = _decode_token(token)
    return {"username": username}

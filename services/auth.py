# auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth")

# Temporary users storage
users = {}

class User(BaseModel):
    username: str
    password: str

# REGISTER
@router.post("/register")
def register(user: User):
    print(user)
    if user.username in users:
        raise HTTPException(status_code=400, detail="User already exists ❌")
    users[user.username] = user.password
    return {"status": "success", "message": "Registration successful ✅"}

# LOGIN
@router.post("/login")
def login(user: User):
    if user.username not in users:
        raise HTTPException(status_code=401, detail="User not found ❌")
    if users[user.username] != user.password:
        raise HTTPException(status_code=401, detail="Incorrect password ❌")
    return {"status": "success", "message": f"Welcome {user.username} 🌱"}

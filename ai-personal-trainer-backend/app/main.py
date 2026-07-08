# This file was regenerated due to earlier formatting issues.
# Minimal working FastAPI backend with SQLite + SQLAlchemy and JWT auth.

import asyncio
import json
import os
import time
from datetime import timedelta

from fastapi import APIRouter


from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from .auth import create_access_token, verify_password
from .database import Database
from .models import User
from .schemas import (
    ChatRequest,
    ChatResponse,
    DietPlanRequest,
    DietPlanResponse,
    LoginRequest,
    ProfileResponse,
    RegisterRequest,
    WorkoutPlanRequest,
    WorkoutPlanResponse,
)

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

from .database import get_db


def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    from jose import jwt

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = get_db()
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


app = FastAPI(title="AI Personal Trainer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/debug/user")
def debug_user(email: str, db: Database = Depends(get_db)):
    # Debug-only: return stored user for local testing
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": user.id, "email": user.email, "name": user.name, "password_hash": user.password_hash}


@app.post("/register")
def register(req: RegisterRequest, db: Database = Depends(get_db)):
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = db.create_user(email=req.email, password=req.password, name=req.name)
    return {"id": user.id, "email": user.email, "name": user.name}


@app.post("/login")
def login(req: LoginRequest, db: Database = Depends(get_db)):
    user = db.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        secret=JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/profile", response_model=ProfileResponse)
def profile(
    current: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    stats = db.get_user_profile_stats(current.id)
    return ProfileResponse(user_id=current.id, email=current.email, name=current.name, stats=stats)


@app.post("/workout-plan", response_model=WorkoutPlanResponse)
def workout_plan(
    req: WorkoutPlanRequest,
    current: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    plan = {
        "exercise": req.exercise,
        "days": req.days,
        "plan": [
            {"day": i + 1, "focus": "form" if i % 2 == 0 else "strength", "sets": 3, "reps": 10}
            for i in range(req.days)
        ],
    }
    db.save_plan(current.id, "workout", plan)
    return WorkoutPlanResponse(plan=plan)


@app.post("/diet-plan", response_model=DietPlanResponse)
def diet_plan(
    req: DietPlanRequest,
    current: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    plan = {
        "goal": req.goal,
        "meals_per_day": req.meals_per_day,
        "plan": [
            {"meal": m + 1, "macro_hint": "protein" if m % 2 == 0 else "carbs", "calories": req.calories_per_meal}
            for m in range(req.meals_per_day)
        ],
    }
    db.save_plan(current.id, "diet", plan)
    return DietPlanResponse(plan=plan)


@app.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    current: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    message = (req.message or "").strip()
    reply = f"AI Trainer (stub): I received your message: '{message}'."
    source = "general"
    confidence = 0.62

    db.save_chat_message(current.id, req.message, reply, source)
    return ChatResponse(reply=reply, source=source, confidence=confidence)


# --- Workout routes (AI fitness tracking) ---
# Replaces the previous stub websocket with the real implementation in app/routes/workout.py
from .routes.workout import router as workout_router

app.include_router(workout_router)

# --- Fix auth/register error due to in-memory singleton DB reset across requests ---
# Ensure the same Database instance is reused by forcing a single import path.


# Frontend integration notes:
# - REST: include JWT in Authorization header: `Authorization: Bearer <token>`
# - WebSocket: connect to ws://localhost:8000/ws/<user_id>



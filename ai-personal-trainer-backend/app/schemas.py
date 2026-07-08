from pydantic import BaseModel
from typing import Optional, List, Any


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileResponse(BaseModel):
    user_id: str
    email: str
    name: str
    stats: dict


class WorkoutPlanRequest(BaseModel):
    exercise: str
    days: int


class WorkoutPlanResponse(BaseModel):
    plan: Any


class DietPlanRequest(BaseModel):
    goal: str
    meals_per_day: int
    calories_per_meal: int


class DietPlanResponse(BaseModel):
    plan: Any


class ChatRequest(BaseModel):
    message: Optional[str] = ""


class ChatResponse(BaseModel):
    reply: str
    source: str
    confidence: float

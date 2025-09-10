from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ClassCreate(BaseModel):
    name: str


class ClassResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClassWithDetails(ClassResponse):
    student_count: int
    recent_activity: Optional[str] = None


class JoinClassRequest(BaseModel):
    invite_code: str


class JoinClassResponse(BaseModel):
    success: bool
    message: str
    class_id: Optional[int] = None

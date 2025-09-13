from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ClassCreate(BaseModel):
    name: str


class ClassRead(BaseModel):
    id: int
    name: str
    teacher_id: int
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClassResponse(ClassRead):
    """Alias for backward compatibility"""
    pass


class ClassWithDetails(ClassRead):
    student_count: int
    recent_activity: Optional[str] = None


class JoinRequest(BaseModel):
    invite_code: str


class JoinClassRequest(JoinRequest):
    """Alias for backward compatibility"""
    pass


class JoinClassResponse(BaseModel):
    success: bool
    message: str
    class_id: Optional[int] = None


class InviteRegenerateResponse(BaseModel):
    success: bool
    invite_code: str
    message: str

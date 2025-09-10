from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuestionCreate(BaseModel):
    type: str  # 'mcq' or 'short'
    prompt: str
    options: Optional[List[str]] = None  # For MCQ
    answer_key: str
    skill_tags: Optional[List[str]] = []


class AssignmentCreate(BaseModel):
    class_id: int
    title: str
    type: str  # 'quiz' or 'written'
    rubric: Optional[Dict[str, Any]] = {}
    due_at: Optional[datetime] = None
    questions: List[QuestionCreate]


class QuestionResponse(BaseModel):
    id: int
    type: str
    prompt: str
    options: Optional[List[str]] = None
    skill_tags: Optional[List[str]] = []

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    id: int
    class_id: int
    title: str
    type: str
    rubric: Optional[Dict[str, Any]] = {}
    due_at: Optional[datetime] = None
    created_at: datetime
    questions: List[QuestionResponse]

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: int
    responses: List[Dict[str, Any]]  # question_id -> answer


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    ai_score: Optional[int] = None
    teacher_score: Optional[int] = None
    ai_explanation: Optional[str] = None

    class Config:
        from_attributes = True

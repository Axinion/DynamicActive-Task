from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class QuestionCreate(BaseModel):
    type: str  # 'mcq' or 'short'
    prompt: str
    options: Optional[List[str]] = None  # For MCQ
    answer_key: Optional[Union[str, List[str]]] = None
    skill_tags: Optional[List[str]] = []


class AssignmentCreate(BaseModel):
    class_id: int
    title: str
    type: str  # 'quiz' or 'written'
    due_at: Optional[datetime] = None
    rubric: Optional[Dict[str, Any]] = None
    questions: List[QuestionCreate]


class QuestionReadLite(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    type: str
    prompt: str
    options: Optional[List[str]] = None
    skill_tags: Optional[List[str]] = []


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    type: str
    prompt: str
    options: Optional[List[str]] = None
    answer_key: Optional[Union[str, List[str]]] = None
    skill_tags: Optional[List[str]] = []


class AssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    class_id: int
    title: str
    type: str
    rubric: Optional[Dict[str, Any]] = None
    due_at: Optional[datetime] = None
    created_at: datetime
    questions: List[QuestionReadLite]


class SubmissionCreate(BaseModel):
    answers: List[Dict[str, Any]]  # [{"question_id": int, "answer": any}]


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    ai_score: Optional[float] = None
    teacher_score: Optional[float] = None


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    submission: SubmissionRead
    breakdown: List[Dict[str, Any]]  # [{"question_id": int, "is_correct": bool|float}]


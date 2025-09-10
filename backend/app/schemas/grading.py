from pydantic import BaseModel
from typing import List, Optional


class GradeRequest(BaseModel):
    question_id: int
    student_answer: str


class GradeResponse(BaseModel):
    ai_score: float  # 0.0 to 1.0
    ai_explanation: str
    confidence: float  # 0.0 to 1.0
    suggested_feedback: Optional[str] = None


class BatchGradeRequest(BaseModel):
    responses: List[GradeRequest]


class BatchGradeResponse(BaseModel):
    results: List[GradeResponse]
    overall_score: float
    overall_explanation: str

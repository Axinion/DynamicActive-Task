"""
Pydantic schemas for teacher override functionality.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ResponseOverrideRequest(BaseModel):
    """Request model for overriding a response score."""
    teacher_score: float = Field(..., ge=0, le=100, description="Teacher score (0-100)")
    teacher_feedback: Optional[str] = Field(None, description="Optional teacher feedback")


class SubmissionOverrideRequest(BaseModel):
    """Request model for overriding a submission score."""
    teacher_score: float = Field(..., ge=0, le=100, description="Teacher score (0-100)")


class ResponseOverrideResponse(BaseModel):
    """Response model for response override."""
    id: int
    submission_id: int
    question_id: int
    student_answer: str
    ai_score: Optional[float]
    teacher_score: Optional[float]
    ai_feedback: Optional[str]
    teacher_feedback: Optional[str]
    matched_keywords: Optional[list]


class SubmissionOverrideResponse(BaseModel):
    """Response model for submission override."""
    id: int
    assignment_id: int
    student_id: int
    submitted_at: str
    ai_score: Optional[float]
    teacher_score: Optional[float]
    ai_explanation: Optional[str]

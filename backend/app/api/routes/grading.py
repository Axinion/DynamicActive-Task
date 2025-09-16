"""
Standalone grading API endpoints for testing and external use.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ...services.grading import score_short_answer


router = APIRouter()


class ShortAnswerGradingRequest(BaseModel):
    """Request model for short answer grading."""
    student_answer: str
    model_answer: str
    rubric_keywords: List[str]


class ShortAnswerGradingResponse(BaseModel):
    """Response model for short answer grading."""
    score: float
    confidence: float
    explanation: str
    matched_keywords: List[str]


@router.post("/short-answer", response_model=ShortAnswerGradingResponse)
async def grade_short_answer(request: ShortAnswerGradingRequest):
    """
    Grade a short answer question using AI.
    
    This endpoint provides standalone grading functionality for testing
    and external integrations.
    
    Args:
        request: Contains student_answer, model_answer, and rubric_keywords
        
    Returns:
        Grading result with score, confidence, explanation, and matched keywords
        
    Example:
        ```json
        {
            "student_answer": "To solve 2x + 3 = 7, I subtract 3 from both sides",
            "model_answer": "Isolate the variable using inverse operations",
            "rubric_keywords": ["isolate", "variable", "inverse", "operations"]
        }
        ```
    """
    try:
        # Use the grading service to score the answer
        result = score_short_answer(
            student_answer=request.student_answer,
            model_answer=request.model_answer,
            rubric_keywords=request.rubric_keywords
        )
        
        return ShortAnswerGradingResponse(
            score=result["score"],
            confidence=result["confidence"],
            explanation=result["explanation"],
            matched_keywords=result["matched_keywords"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during grading: {str(e)}"
        )


@router.get("/health")
async def grading_health_check():
    """
    Health check endpoint for the grading service.
    
    Returns:
        Status information about the grading service
    """
    try:
        # Test the grading service with a simple example
        test_result = score_short_answer(
            student_answer="Test answer",
            model_answer="Test model answer",
            rubric_keywords=["test", "keyword"]
        )
        
        return {
            "status": "healthy",
            "service": "grading",
            "version": "1.0.0",
            "test_score": test_result["score"],
            "message": "Grading service is operational"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Grading service unhealthy: {str(e)}"
        )
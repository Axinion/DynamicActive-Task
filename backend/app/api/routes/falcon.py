"""
API routes for Falcon-H1-1B-Base model services.
Provides enhanced AI capabilities for feedback generation and analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ...db.session import get_db
from ...core.security import get_current_user
from ...services.falcon_service import (
    generate_feedback, 
    generate_learning_tips, 
    analyze_misconception_pattern,
    get_model_info,
    clear_model_cache
)

router = APIRouter()


class FeedbackRequest(BaseModel):
    student_answer: str
    model_answer: str
    question_prompt: str
    rubric_keywords: List[str]
    score: float


class LearningTipsRequest(BaseModel):
    student_answer: str
    model_answer: str
    skill_tags: List[str]
    misconceptions: List[str] = []


class MisconceptionAnalysisRequest(BaseModel):
    responses: List[str]
    question_prompts: List[str]
    skill_tags: List[str]


@router.post("/feedback")
async def generate_enhanced_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate enhanced feedback using Falcon-H1-1B-Base model.
    
    This endpoint provides more sophisticated and personalized feedback
    compared to the standard grading service.
    """
    try:
        feedback = generate_feedback(
            student_answer=request.student_answer,
            model_answer=request.model_answer,
            question_prompt=request.question_prompt,
            rubric_keywords=request.rubric_keywords,
            score=request.score
        )
        
        return {
            "feedback": feedback,
            "model_used": "Falcon-H1-1B-Base",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {str(e)}"
        )


@router.post("/learning-tips")
async def generate_personalized_tips(
    request: LearningTipsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized learning tips using Falcon-H1-1B-Base model.
    
    Provides structured learning suggestions including praise, 
    improvement suggestions, and study tips.
    """
    try:
        tips = generate_learning_tips(
            student_answer=request.student_answer,
            model_answer=request.model_answer,
            skill_tags=request.skill_tags,
            misconceptions=request.misconceptions
        )
        
        return {
            "learning_tips": tips,
            "model_used": "Falcon-H1-1B-Base",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate learning tips: {str(e)}"
        )


@router.post("/analyze-misconceptions")
async def analyze_misconception_patterns(
    request: MisconceptionAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze misconception patterns using Falcon-H1-1B-Base model.
    
    This endpoint helps teachers identify common patterns in student
    misconceptions and provides insights for remediation.
    """
    # Verify user is a teacher
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access misconception analysis"
        )
    
    try:
        analysis = analyze_misconception_pattern(
            responses=request.responses,
            question_prompts=request.question_prompts,
            skill_tags=request.skill_tags
        )
        
        return {
            "analysis": analysis,
            "model_used": "Falcon-H1-1B-Base",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze misconceptions: {str(e)}"
        )


@router.get("/model-info")
async def get_falcon_model_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about the loaded Falcon model.
    
    Provides details about model status, device, and configuration.
    """
    try:
        model_info = get_model_info()
        return {
            "model_info": model_info,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_falcon_cache(
    current_user: dict = Depends(get_current_user)
):
    """
    Clear the Falcon model cache.
    
    Useful for memory management and forcing model reload.
    """
    # Verify user is a teacher or admin
    if current_user["role"] not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can clear model cache"
        )
    
    try:
        clear_model_cache()
        return {
            "message": "Model cache cleared successfully",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/health")
async def falcon_health_check():
    """
    Health check endpoint for the Falcon service.
    """
    try:
        model_info = get_model_info()
        return {
            "status": "ok" if model_info.get("model_loaded", False) else "degraded",
            "message": "Falcon service is operational" if model_info.get("model_loaded", False) else "Falcon model not loaded",
            "model_info": model_info,
            "features": [
                "enhanced_feedback_generation",
                "personalized_learning_tips",
                "misconception_pattern_analysis",
                "text_generation"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Falcon service error: {str(e)}",
            "model_info": {"model_loaded": False, "error": str(e)},
            "features": []
        }


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...db.models import User, Question
from ...schemas.grading import GradeRequest, GradeResponse, BatchGradeRequest, BatchGradeResponse
from ...core.security import get_current_user

router = APIRouter()


@router.post("/short-answer", response_model=GradeResponse)
async def grade_short_answer(
    request: GradeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grade a short answer question using AI."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade assignments")
    
    # Get the question
    question = db.query(Question).filter(Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # For now, return a placeholder response
    # In a real implementation, this would call the AI grading service
    ai_score = 0.75  # Placeholder score
    ai_explanation = f"Student answer shows understanding of key concepts. The response addresses the main points: {request.student_answer[:50]}..."
    confidence = 0.85  # Placeholder confidence
    
    return GradeResponse(
        ai_score=ai_score,
        ai_explanation=ai_explanation,
        confidence=confidence,
        suggested_feedback="Good work! Consider expanding on the second point for a more complete answer."
    )


@router.post("/batch", response_model=BatchGradeResponse)
async def batch_grade(
    request: BatchGradeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grade multiple responses in batch."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade assignments")
    
    results = []
    total_score = 0.0
    
    for grade_request in request.responses:
        # Get the question
        question = db.query(Question).filter(Question.id == grade_request.question_id).first()
        if not question:
            continue
        
        # Placeholder grading logic
        ai_score = 0.75  # Placeholder score
        ai_explanation = f"Student answer shows understanding of key concepts. The response addresses the main points: {grade_request.student_answer[:50]}..."
        confidence = 0.85  # Placeholder confidence
        
        results.append(GradeResponse(
            ai_score=ai_score,
            ai_explanation=ai_explanation,
            confidence=confidence,
            suggested_feedback="Good work! Consider expanding on the second point for a more complete answer."
        ))
        
        total_score += ai_score
    
    overall_score = total_score / len(results) if results else 0.0
    overall_explanation = f"Overall performance: {overall_score:.1%}. Student demonstrates good understanding of the material with room for improvement in detail and depth."
    
    return BatchGradeResponse(
        results=results,
        overall_score=overall_score,
        overall_explanation=overall_explanation
    )

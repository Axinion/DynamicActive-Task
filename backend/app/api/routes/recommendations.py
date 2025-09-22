"""
API routes for personalized recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...db.session import get_db
from ...db.models import User, Class, Enrollment
from ...core.security import get_current_user
from ...services.recommendations import get_student_recommendations

router = APIRouter()


@router.get("")
@router.get("/")
async def get_recommendations(
    class_id: int = Query(..., description="Class ID is required"),
    student_id: Optional[int] = Query(None, description="Student ID (optional, defaults to current user)"),
    k: int = Query(3, ge=1, le=10, description="Number of recommendations to return (1-10)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized lesson recommendations for a student.
    
    Teachers can view recommendations for any student in their class.
    Students can only view their own recommendations.
    """
    # Determine the target student ID
    target_student_id = student_id if student_id is not None else current_user["id"]
    
    # Verify the class exists
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check permissions
    if current_user["role"] == "student":
        # Students can only view their own recommendations
        if target_student_id != current_user["id"]:
            raise HTTPException(
                status_code=403, 
                detail="Students can only view their own recommendations"
            )
        
        # Verify student is enrolled in the class
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user["id"],
            Enrollment.class_id == class_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=403,
                detail="You are not enrolled in this class"
            )
    
    elif current_user["role"] == "teacher":
        # Teachers can view recommendations for any student in their class
        if class_.teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="You can only view recommendations for students in your own classes"
            )
        
        # Verify the target student is enrolled in the class
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == target_student_id,
            Enrollment.class_id == class_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=404,
                detail="Student not found in this class"
            )
    
    else:
        raise HTTPException(status_code=403, detail="Invalid user role")
    
    # Get the target student info
    target_student = db.query(User).filter(User.id == target_student_id).first()
    if not target_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get recommendations
    try:
        recommendations_data = get_student_recommendations(
            student_id=target_student_id,
            class_id=class_id,
            db=db,
            k=k
        )
        
        # Add metadata
        recommendations_data.update({
            'requested_by': {
                'id': current_user["id"],
                'name': current_user["name"],
                'role': current_user["role"]
            },
            'target_student': {
                'id': target_student.id,
                'name': target_student.name,
                'email': target_student.email
            }
        })
        
        return recommendations_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/health")
async def recommendations_health_check():
    """
    Health check endpoint for the recommendations service.
    """
    return {
        "status": "ok",
        "message": "Recommendations service is operational",
        "features": [
            "skill_mastery_computation",
            "content_similarity_scoring",
            "personalized_lesson_ranking"
        ]
    }
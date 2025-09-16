"""
API routes for student progress tracking and skill mastery analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...db.session import get_db
from ...db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from ...core.security import get_current_user
from ...services.progress import get_student_skill_mastery

router = APIRouter()


@router.get("/skills")
async def get_student_progress_api(
    class_id: int = Query(..., description="Class ID is required"),
    student_id: int = Query(..., description="Student ID is required"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get student progress by skill tags with mastery scores (0-1).
    
    Students can request their own progress; teachers can request for any student in their class.
    
    Args:
        class_id: ID of the class
        student_id: ID of the student
    """
    # Verify user has access to this data
    if current_user["role"] == "student":
        # Students can only access their own progress
        if current_user["id"] != student_id:
            raise HTTPException(
                status_code=403,
                detail="Students can only access their own progress"
            )
    elif current_user["role"] == "teacher":
        # Teachers can access any student in their class
        # Verify the class exists and teacher owns it
        class_ = db.query(Class).filter(
            Class.id == class_id,
            Class.teacher_id == current_user["id"]
        ).first()
        
        if not class_:
            raise HTTPException(
                status_code=404,
                detail="Class not found or access denied"
            )
        
        # Verify student is enrolled in the class
        enrollment = db.query(Enrollment).filter(
            Enrollment.class_id == class_id,
            Enrollment.student_id == student_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=404,
                detail="Student not found in this class"
            )
    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )
    
    # Verify student exists
    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student"
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    try:
        # Get skill mastery data
        progress_data = get_student_skill_mastery(class_id, student_id, db)
        
        # Add metadata
        progress_data.update({
            'student': {
                'id': student.id,
                'name': student.name,
                'email': student.email
            },
            'class_id': class_id,
            'requested_by': {
                'id': current_user["id"],
                'name': current_user["name"],
                'role': current_user["role"]
            }
        })
        
        return progress_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating student progress: {str(e)}"
        )


@router.get("/health")
async def progress_health_check():
    """
    Health check endpoint for the progress service.
    """
    return {
        "status": "ok",
        "message": "Progress service is operational",
        "features": [
            "skill_mastery_tracking",
            "progress_analysis",
            "performance_metrics"
        ]
    }

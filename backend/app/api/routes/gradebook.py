from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.session import get_db
from ...db.models import User, Class, Assignment, Submission, Response
from ...core.security import get_current_user

router = APIRouter()


@router.get("/")
async def get_gradebook(
    class_id: int = Query(..., description="Class ID is required"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get gradebook for a specific class (teacher only)."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access gradebook")
    
    # Verify teacher owns the class
    class_ = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user["id"]
    ).first()
    
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found or access denied")
    
    # Query submissions with joins to get assignment and student details
    submissions = db.query(
        Submission.id.label("submission_id"),
        Assignment.id.label("assignment_id"),
        Assignment.title.label("assignment_title"),
        User.id.label("student_id"),
        User.name.label("student_name"),
        User.email.label("student_email"),
        Submission.submitted_at,
        Submission.ai_score,
        Submission.teacher_score,
        Submission.ai_explanation
    ).join(
        Assignment, Submission.assignment_id == Assignment.id
    ).join(
        User, Submission.student_id == User.id
    ).filter(
        Assignment.class_id == class_id
    ).order_by(
        Assignment.title, User.name
    ).all()
    
    # Convert to list of dictionaries
    gradebook_entries = []
    for submission in submissions:
        gradebook_entries.append({
            "submission_id": submission.submission_id,
            "assignment_id": submission.assignment_id,
            "assignment_title": submission.assignment_title,
            "student_id": submission.student_id,
            "student_name": submission.student_name,
            "student_email": submission.student_email,
            "submitted_at": submission.submitted_at,
            "ai_score": submission.ai_score,
            "teacher_score": submission.teacher_score,
            "ai_explanation": submission.ai_explanation
        })
    
    return {
        "class_id": class_id,
        "class_name": class_.name,
        "total_submissions": len(gradebook_entries),
        "submissions": gradebook_entries
    }

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
from ...db.session import get_db
from ...db.models import User, Class, Assignment, Submission, Response, Question
from ...core.security import get_current_user
from ...schemas.overrides import (
    ResponseOverrideRequest, 
    SubmissionOverrideRequest,
    ResponseOverrideResponse,
    SubmissionOverrideResponse
)

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


@router.post("/responses/{response_id}/override", response_model=ResponseOverrideResponse)
async def override_response_score(
    response_id: int,
    override_data: ResponseOverrideRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Override a response score (teacher only)."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can override scores")
    
    # Get the response with related data
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Get the submission and assignment to verify teacher ownership
    submission = db.query(Submission).filter(Submission.id == response.submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify teacher owns the class
    class_ = db.query(Class).filter(
        Class.id == assignment.class_id,
        Class.teacher_id == current_user["id"]
    ).first()
    
    if not class_:
        raise HTTPException(status_code=403, detail="Access denied - you don't own this class")
    
    # Update the response
    response.teacher_score = override_data.teacher_score
    if override_data.teacher_feedback is not None:
        response.teacher_feedback = override_data.teacher_feedback
    
    db.commit()
    db.refresh(response)
    
    return ResponseOverrideResponse(
        id=response.id,
        submission_id=response.submission_id,
        question_id=response.question_id,
        student_answer=response.student_answer,
        ai_score=response.ai_score,
        teacher_score=response.teacher_score,
        ai_feedback=response.ai_feedback,
        teacher_feedback=response.teacher_feedback,
        matched_keywords=response.matched_keywords
    )


@router.post("/submissions/{submission_id}/override", response_model=SubmissionOverrideResponse)
async def override_submission_score(
    submission_id: int,
    override_data: SubmissionOverrideRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Override a submission score (teacher only)."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can override scores")
    
    # Get the submission with related data
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Get the assignment to verify teacher ownership
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify teacher owns the class
    class_ = db.query(Class).filter(
        Class.id == assignment.class_id,
        Class.teacher_id == current_user["id"]
    ).first()
    
    if not class_:
        raise HTTPException(status_code=403, detail="Access denied - you don't own this class")
    
    # Update the submission
    submission.teacher_score = override_data.teacher_score
    
    db.commit()
    db.refresh(submission)
    
    return SubmissionOverrideResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        submitted_at=submission.submitted_at.isoformat(),
        ai_score=submission.ai_score,
        teacher_score=submission.teacher_score,
        ai_explanation=submission.ai_explanation
    )


@router.get("/export.csv")
async def export_gradebook_csv(
    class_id: int = Query(..., description="Class ID is required"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export gradebook as CSV (teacher only)."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can export gradebook")
    
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
        Assignment.title, User.name, Submission.submitted_at
    ).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Submission ID',
        'Student ID', 
        'Student Name',
        'Student Email',
        'Assignment ID',
        'Assignment Title',
        'Submitted At',
        'AI Score',
        'Teacher Score',
        'Final Score',
        'AI Explanation'
    ])
    
    # Write data rows
    for submission in submissions:
        # Determine final score (teacher score takes precedence)
        final_score = submission.teacher_score if submission.teacher_score is not None else submission.ai_score
        
        writer.writerow([
            submission.submission_id,
            submission.student_id,
            submission.student_name,
            submission.student_email,
            submission.assignment_id,
            submission.assignment_title,
            submission.submitted_at.isoformat() if submission.submitted_at else '',
            submission.ai_score,
            submission.teacher_score,
            final_score,
            submission.ai_explanation or ''
        ])
    
    # Prepare response
    output.seek(0)
    csv_content = output.getvalue()
    output.close()
    
    # Create streaming response
    def generate():
        yield csv_content
    
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=gradebook_class_{class_id}.csv"
        }
    )

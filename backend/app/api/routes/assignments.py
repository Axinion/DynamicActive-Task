from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ...db.session import get_db
from ...db.models import User, Assignment, Question, Submission, Response, Class, Enrollment
from ...schemas.assignments import (
    AssignmentCreate, AssignmentResponse, SubmissionCreate, SubmissionResponse
)
from ...core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new assignment (teacher only)."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    
    # Verify teacher owns the class
    class_ = db.query(Class).filter(
        Class.id == assignment_data.class_id,
        Class.teacher_id == current_user["id"]
    ).first()
    
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found or access denied")
    
    # Create assignment
    new_assignment = Assignment(
        class_id=assignment_data.class_id,
        title=assignment_data.title,
        type=assignment_data.type,
        rubric=assignment_data.rubric or {},
        due_at=assignment_data.due_at
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    # Create questions
    for question_data in assignment_data.questions:
        question = Question(
            assignment_id=new_assignment.id,
            type=question_data.type,
            prompt=question_data.prompt,
            options=question_data.options,
            answer_key=question_data.answer_key,
            skill_tags=question_data.skill_tags or []
        )
        db.add(question)
    
    db.commit()
    db.refresh(new_assignment)
    
    return AssignmentResponse.model_validate(new_assignment)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific assignment."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check access permissions
    if current_user["role"] == "teacher":
        class_ = db.query(Class).filter(
            Class.id == assignment.class_id,
            Class.teacher_id == current_user["id"]
        ).first()
        if not class_:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        # Check if student is enrolled in the class
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user["id"],
            Enrollment.class_id == assignment.class_id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return AssignmentResponse.model_validate(assignment)


@router.post("/{assignment_id}/submit", response_model=SubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    submission_data: SubmissionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an assignment (student only)."""
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    # Verify assignment exists and student has access
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if student is enrolled in the class
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user["id"],
        Enrollment.class_id == assignment.class_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already submitted
    existing_submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user["id"]
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="Assignment already submitted")
    
    # Create submission
    submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user["id"]
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Create responses
    for response_data in submission_data.responses:
        response = Response(
            submission_id=submission.id,
            question_id=response_data["question_id"],
            student_answer=response_data["answer"]
        )
        db.add(response)
    
    db.commit()
    db.refresh(submission)
    
    return SubmissionResponse.model_validate(submission)


@router.get("/", response_model=List[AssignmentResponse])
async def get_assignments(
    class_id: int = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignments for current user."""
    if current_user["role"] == "teacher":
        # Teachers can see assignments from their classes
        query = db.query(Assignment).join(Class).filter(Class.teacher_id == current_user["id"])
        if class_id:
            query = query.filter(Assignment.class_id == class_id)
    else:
        # Students can see assignments from classes they're enrolled in
        query = db.query(Assignment).join(Class).join(Enrollment).filter(
            Enrollment.user_id == current_user["id"]
        )
        if class_id:
            query = query.filter(Assignment.class_id == class_id)
    
    assignments = query.all()
    return [AssignmentResponse.model_validate(assignment) for assignment in assignments]

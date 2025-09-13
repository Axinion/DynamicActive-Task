from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
from ...db.session import get_db
from ...db.models import User, Assignment, Question, Submission, Response, Class, Enrollment
from ...schemas.assignments import (
    AssignmentCreate, AssignmentRead, SubmissionCreate, SubmissionResponse, SubmissionRead
)
from ...core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=AssignmentRead)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new assignment with questions (teacher only)."""
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
        rubric=assignment_data.rubric,
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
            answer_key=json.dumps(question_data.answer_key) if question_data.answer_key else None,
            skill_tags=question_data.skill_tags or []
        )
        db.add(question)
    
    db.commit()
    db.refresh(new_assignment)
    
    return AssignmentRead.model_validate(new_assignment)


@router.get("/", response_model=List[AssignmentRead])
async def get_assignments(
    class_id: int = Query(..., description="Class ID is required"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignments for a specific class."""
    if current_user["role"] == "teacher":
        # Teachers can see assignments from their classes
        query = db.query(Assignment).join(Class).filter(
            Class.teacher_id == current_user["id"],
            Assignment.class_id == class_id
        )
    else:
        # Students can see assignments from classes they're enrolled in
        query = db.query(Assignment).join(Class).join(Enrollment).filter(
            Enrollment.user_id == current_user["id"],
            Assignment.class_id == class_id
        )
    
    assignments = query.all()
    return [AssignmentRead.model_validate(assignment) for assignment in assignments]


@router.get("/{assignment_id}", response_model=AssignmentRead)
async def get_assignment(
    assignment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific assignment with questions."""
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
    
    return AssignmentRead.model_validate(assignment)


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
    
    # Get all questions for this assignment
    questions = db.query(Question).filter(Question.assignment_id == assignment_id).all()
    question_dict = {q.id: q for q in questions}
    
    # Create responses and auto-grade MCQ questions
    total_score = 0
    scored_questions = 0
    breakdown = []
    
    for answer_data in submission_data.answers:
        question_id = answer_data["question_id"]
        student_answer = answer_data["answer"]
        
        if question_id not in question_dict:
            raise HTTPException(status_code=400, detail=f"Question {question_id} not found in assignment")
        
        question = question_dict[question_id]
        
        # Create response
        response = Response(
            submission_id=submission.id,
            question_id=question_id,
            student_answer=json.dumps(student_answer) if isinstance(student_answer, (list, dict)) else str(student_answer)
        )
        
        # Auto-grade MCQ questions
        if question.type == "mcq":
            try:
                answer_key = json.loads(question.answer_key) if question.answer_key else None
                if answer_key is not None:
                    is_correct = student_answer == answer_key
                    response.ai_score = 100.0 if is_correct else 0.0
                    total_score += response.ai_score
                    scored_questions += 1
                    breakdown.append({
                        "question_id": question_id,
                        "is_correct": is_correct,
                        "score": response.ai_score
                    })
                else:
                    breakdown.append({
                        "question_id": question_id,
                        "is_correct": None,
                        "score": None
                    })
            except (json.JSONDecodeError, TypeError):
                breakdown.append({
                    "question_id": question_id,
                    "is_correct": None,
                    "score": None
                })
        else:  # short answer questions
            response.ai_score = None  # Will be graded later
            breakdown.append({
                "question_id": question_id,
                "is_correct": None,
                "score": None
            })
        
        db.add(response)
    
    # Calculate overall AI score for MCQ questions
    if scored_questions > 0:
        submission.ai_score = total_score / scored_questions
        submission.ai_explanation = f"Auto-graded {scored_questions} multiple choice questions"
    
    db.commit()
    db.refresh(submission)
    
    return SubmissionResponse(
        submission=SubmissionRead.model_validate(submission),
        breakdown=breakdown
    )

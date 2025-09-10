from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets
import string
from ..db.session import get_db
from ..db.models import User, Class, Enrollment
from ..schemas.classes import ClassCreate, ClassResponse, ClassWithDetails, JoinClassRequest, JoinClassResponse
from .auth import get_current_user_simple

router = APIRouter()


@router.post("/", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """Create a new class (teacher only)."""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create classes")
    
    # Generate unique invite code
    invite_code = ''.join(secrets.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Ensure invite code is unique
    while db.query(Class).filter(Class.invite_code == invite_code).first():
        invite_code = ''.join(secrets.choices(string.ascii_uppercase + string.digits, k=6))
    
    new_class = Class(
        name=class_data.name,
        teacher_id=current_user.id,
        invite_code=invite_code
    )
    
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return ClassResponse.model_validate(new_class)


@router.get("/", response_model=List[ClassWithDetails])
async def get_classes(
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """Get classes for current user."""
    if current_user.role == "teacher":
        # Get classes taught by teacher
        classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
        result = []
        for cls in classes:
            student_count = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()
            result.append(ClassWithDetails(
                **cls.__dict__,
                student_count=student_count,
                recent_activity="2 assignments due"  # Mock data
            ))
        return result
    else:
        # Get classes student is enrolled in
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()
        result = []
        for enrollment in enrollments:
            cls = db.query(Class).filter(Class.id == enrollment.class_id).first()
            if cls:
                student_count = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()
                result.append(ClassWithDetails(
                    **cls.__dict__,
                    student_count=student_count,
                    recent_activity="Math Quiz - Tomorrow"  # Mock data
                ))
        return result


@router.post("/join", response_model=JoinClassResponse)
async def join_class(
    request: JoinClassRequest,
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """Join a class using invite code (student only)."""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can join classes")
    
    # Find class by invite code
    class_to_join = db.query(Class).filter(Class.invite_code == request.invite_code).first()
    
    if not class_to_join:
        return JoinClassResponse(
            success=False,
            message="Invalid invite code"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.class_id == class_to_join.id
    ).first()
    
    if existing_enrollment:
        return JoinClassResponse(
            success=False,
            message="Already enrolled in this class"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        class_id=class_to_join.id
    )
    
    db.add(enrollment)
    db.commit()
    
    return JoinClassResponse(
        success=True,
        message="Successfully joined class",
        class_id=class_to_join.id
    )


@router.get("/{class_id}/invite", response_model=dict)
async def get_invite_code(
    class_id: int,
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """Get invite code for a class (teacher only)."""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access invite codes")
    
    cls = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return {"invite_code": cls.invite_code}

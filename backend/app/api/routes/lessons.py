from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.session import get_db
from ...db.models import User, Lesson, Class, Enrollment
from ...schemas.lessons import LessonCreate, LessonRead, LessonWithClass
from ...core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=LessonRead)
async def create_lesson(
    lesson_data: LessonCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lesson (teacher only)."""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create lessons")
    
    # Verify teacher owns the class
    class_ = db.query(Class).filter(
        Class.id == lesson_data.class_id,
        Class.teacher_id == current_user["id"]
    ).first()
    
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found or access denied")
    
    new_lesson = Lesson(
        class_id=lesson_data.class_id,
        title=lesson_data.title,
        content=lesson_data.content,
        skill_tags=lesson_data.skill_tags or []
    )
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return LessonRead.model_validate(new_lesson)


@router.get("", response_model=List[LessonWithClass])
@router.get("/", response_model=List[LessonWithClass])
async def get_lessons(
    class_id: int = Query(..., description="Class ID is required"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lessons for a specific class. Returns lessons sorted by created_at DESC."""
    if current_user["role"] == "teacher":
        # Teachers can see lessons from their classes
        query = db.query(Lesson).join(Class).filter(
            Class.teacher_id == current_user["id"],
            Lesson.class_id == class_id
        )
    else:
        # Students can see lessons from classes they're enrolled in
        query = db.query(Lesson).join(Class).join(Enrollment).filter(
            Enrollment.user_id == current_user["id"],
            Lesson.class_id == class_id
        )
    
    # Sort by created_at DESC
    lessons = query.order_by(Lesson.created_at.desc()).all()
    
    result = []
    for lesson in lessons:
        class_ = db.query(Class).filter(Class.id == lesson.class_id).first()
        result.append(LessonWithClass(
            **lesson.__dict__,
            class_name=class_.name if class_ else "Unknown Class"
        ))
    
    return result


@router.get("/{lesson_id}", response_model=LessonWithClass)
async def get_lesson(
    lesson_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific lesson."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check access permissions
    if current_user["role"] == "teacher":
        class_ = db.query(Class).filter(
            Class.id == lesson.class_id,
            Class.teacher_id == current_user["id"]
        ).first()
        if not class_:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        # Check if student is enrolled in the class
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user["id"],
            Enrollment.class_id == lesson.class_id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Access denied")
    
    class_ = db.query(Class).filter(Class.id == lesson.class_id).first()
    return LessonWithClass(
        **lesson.__dict__,
        class_name=class_.name if class_ else "Unknown Class"
    )

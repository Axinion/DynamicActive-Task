from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..db.session import get_db
from ..db.models import User, Lesson, Class, Enrollment
from ..schemas.recommendations import RecommendationResponse, LessonRecommendation
from ..core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=RecommendationResponse)
async def get_recommendations(
    student_id: int = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered lesson recommendations for a student."""
    # For teachers, they can specify a student_id
    # For students, they can only get their own recommendations
    if current_user["role"] == "teacher":
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id required for teachers")
        target_student_id = student_id
    else:
        target_student_id = current_user["id"]
    
    # Get student's enrolled classes
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == target_student_id).all()
    class_ids = [enrollment.class_id for enrollment in enrollments]
    
    if not class_ids:
        return RecommendationResponse(
            student_id=target_student_id,
            recommendations=[],
            based_on="No enrolled classes"
        )
    
    # Get lessons from enrolled classes
    lessons = db.query(Lesson).filter(Lesson.class_id.in_(class_ids)).limit(10).all()
    
    # For now, return mock recommendations
    # In a real implementation, this would use AI to analyze student performance
    # and recommend lessons based on skill gaps, learning patterns, etc.
    
    recommendations = []
    for i, lesson in enumerate(lessons[:3]):  # Return top 3 recommendations
        class_ = db.query(Class).filter(Class.id == lesson.class_id).first()
        
        why_reasons = [
            "Based on your recent quiz performance, this lesson will help strengthen your understanding of key concepts.",
            "This lesson builds on topics you've shown interest in and will prepare you for upcoming assignments.",
            "Recommended to address knowledge gaps identified in your recent submissions."
        ]
        
        recommendations.append(LessonRecommendation(
            id=lesson.id,
            title=lesson.title,
            content=lesson.content[:200] + "..." if len(lesson.content) > 200 else lesson.content,
            class_name=class_.name if class_ else "Unknown Class",
            why=why_reasons[i % len(why_reasons)],
            skill_tags=lesson.skill_tags or [],
            difficulty_score=0.6 + (i * 0.1)  # Mock difficulty scores
        ))
    
    return RecommendationResponse(
        student_id=target_student_id,
        recommendations=recommendations,
        based_on="Recent performance analysis and skill gap identification"
    )


@router.get("/lessons", response_model=List[LessonRecommendation])
async def get_lesson_recommendations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lesson recommendations for current user (simplified endpoint)."""
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can get lesson recommendations")
    
    # Get student's enrolled classes
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user["id"]).all()
    class_ids = [enrollment.class_id for enrollment in enrollments]
    
    if not class_ids:
        return []
    
    # Get lessons from enrolled classes
    lessons = db.query(Lesson).filter(Lesson.class_id.in_(class_ids)).limit(3).all()
    
    recommendations = []
    for lesson in lessons:
        class_ = db.query(Class).filter(Class.id == lesson.class_id).first()
        
        recommendations.append(LessonRecommendation(
            id=lesson.id,
            title=lesson.title,
            content=lesson.content[:200] + "..." if len(lesson.content) > 200 else lesson.content,
            class_name=class_.name if class_ else "Unknown Class",
            why="Recommended based on your learning progress and upcoming assignments",
            skill_tags=lesson.skill_tags or [],
            difficulty_score=0.7
        ))
    
    return recommendations

"""
API routes for mini-lesson suggestions and re-teach recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from ...db.session import get_db
from ...db.models import User, Class, Lesson, Assignment, Question, Submission, Response, Enrollment
from ...core.security import get_current_user

router = APIRouter()


@router.get("/mini-lessons")
async def get_mini_lesson_suggestions_api(
    class_id: int = Query(..., description="Class ID is required"),
    tags: str = Query(..., description="Comma-separated skill tags (e.g., 'fractions,decimals')"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mini-lesson suggestions for specific skill tags (teacher only).
    
    Returns up to 3 lessons per requested tag, ranked by:
    1. Tag match (exact match preferred)
    2. Recency (newest first)
    
    Args:
        class_id: ID of the class
        tags: Comma-separated list of skill tags to find lessons for
    """
    # Verify user is a teacher
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=403, 
            detail="Only teachers can access mini-lesson suggestions"
        )
    
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
    
    # Parse tags
    if not tags or not tags.strip():
        raise HTTPException(
            status_code=422,
            detail="Tags parameter is required and cannot be empty"
        )
    
    requested_tags = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
    
    if not requested_tags:
        raise HTTPException(
            status_code=422,
            detail="At least one valid tag is required"
        )
    
    try:
        # Get lessons for the class
        lessons = db.query(Lesson).filter(
            Lesson.class_id == class_id
        ).order_by(Lesson.created_at.desc()).all()
        
        # Group lessons by tag match
        tag_suggestions = []
        
        for tag in requested_tags:
            matching_lessons = []
            
            for lesson in lessons:
                # Parse lesson skill tags
                lesson_tags = []
                if lesson.skill_tags:
                    try:
                        if isinstance(lesson.skill_tags, str):
                            lesson_tags = json.loads(lesson.skill_tags)
                        else:
                            lesson_tags = lesson.skill_tags
                    except (json.JSONDecodeError, TypeError):
                        lesson_tags = []
                
                # Convert to lowercase for comparison
                lesson_tags_lower = [t.lower() for t in lesson_tags]
                
                # Check for tag match
                if tag in lesson_tags_lower:
                    matching_lessons.append({
                        'lesson_id': lesson.id,
                        'title': lesson.title,
                        'created_at': lesson.created_at,
                        'tag_match_score': 1.0  # Exact match
                    })
                else:
                    # Check for partial match (contains the tag)
                    for lesson_tag in lesson_tags_lower:
                        if tag in lesson_tag or lesson_tag in tag:
                            matching_lessons.append({
                                'lesson_id': lesson.id,
                                'title': lesson.title,
                                'created_at': lesson.created_at,
                                'tag_match_score': 0.5  # Partial match
                            })
                            break
            
            # Sort by tag match score (exact matches first), then by recency
            matching_lessons.sort(
                key=lambda x: (-x['tag_match_score'], -x['created_at'].timestamp())
            )
            
            # Take up to 3 lessons
            top_lessons = matching_lessons[:3]
            
            # Format response
            tag_suggestions.append({
                'tag': tag,
                'lessons': [
                    {
                        'lesson_id': lesson['lesson_id'],
                        'title': lesson['title']
                    }
                    for lesson in top_lessons
                ],
                'total_matches': len(matching_lessons),
                'exact_matches': len([l for l in matching_lessons if l['tag_match_score'] == 1.0])
            })
        
        return {
            'class_id': class_id,
            'class_name': class_.name,
            'requested_tags': requested_tags,
            'suggestions': tag_suggestions,
            'requested_by': {
                'id': current_user["id"],
                'name': current_user["name"],
                'role': current_user["role"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating mini-lesson suggestions: {str(e)}"
        )


@router.get("/mini-lessons/weak-skills")
async def get_mini_lessons_for_weak_skills_api(
    class_id: int = Query(..., description="Class ID is required"),
    student_id: int = Query(..., description="Student ID is required"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mini-lesson suggestions for a student's weak skills (teacher only).
    
    Automatically identifies weak skills from student performance and suggests
    relevant lessons for remediation.
    """
    # Verify user is a teacher
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=403, 
            detail="Only teachers can access mini-lesson suggestions"
        )
    
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
    
    try:
        # Import here to avoid circular imports
        from ...services.progress import get_student_skill_mastery
        
        # Get student's skill mastery
        progress_data = get_student_skill_mastery(class_id, student_id, db)
        
        # Identify weak skills (mastery < 0.6)
        weak_skills = [
            skill for skill in progress_data['skill_mastery'] 
            if skill['mastery'] < 0.6
        ]
        
        if not weak_skills:
            return {
                'class_id': class_id,
                'student_id': student_id,
                'student_name': db.query(User).filter(User.id == student_id).first().name,
                'weak_skills': [],
                'suggestions': [],
                'message': 'No weak skills identified. Student is performing well!'
            }
        
        # Get lessons for the class
        lessons = db.query(Lesson).filter(
            Lesson.class_id == class_id
        ).order_by(Lesson.created_at.desc()).all()
        
        # Generate suggestions for each weak skill
        suggestions = []
        
        for weak_skill in weak_skills:
            tag = weak_skill['tag']
            matching_lessons = []
            
            for lesson in lessons:
                # Parse lesson skill tags
                lesson_tags = []
                if lesson.skill_tags:
                    try:
                        if isinstance(lesson.skill_tags, str):
                            lesson_tags = json.loads(lesson.skill_tags)
                        else:
                            lesson_tags = lesson.skill_tags
                    except (json.JSONDecodeError, TypeError):
                        lesson_tags = []
                
                # Convert to lowercase for comparison
                lesson_tags_lower = [t.lower() for t in lesson_tags]
                
                # Check for tag match
                if tag.lower() in lesson_tags_lower:
                    matching_lessons.append({
                        'lesson_id': lesson.id,
                        'title': lesson.title,
                        'created_at': lesson.created_at,
                        'tag_match_score': 1.0
                    })
            
            # Sort by recency (newest first)
            matching_lessons.sort(key=lambda x: -x['created_at'].timestamp())
            
            # Take up to 3 lessons
            top_lessons = matching_lessons[:3]
            
            suggestions.append({
                'tag': tag,
                'mastery': weak_skill['mastery'],
                'samples': weak_skill['samples'],
                'lessons': [
                    {
                        'lesson_id': lesson['lesson_id'],
                        'title': lesson['title']
                    }
                    for lesson in top_lessons
                ]
            })
        
        return {
            'class_id': class_id,
            'student_id': student_id,
            'student_name': db.query(User).filter(User.id == student_id).first().name,
            'weak_skills': [{'tag': s['tag'], 'mastery': s['mastery'], 'samples': s['samples']} for s in weak_skills],
            'suggestions': suggestions,
            'requested_by': {
                'id': current_user["id"],
                'name': current_user["name"],
                'role': current_user["role"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating mini-lesson suggestions for weak skills: {str(e)}"
        )


@router.get("/health")
async def suggestions_health_check():
    """
    Health check endpoint for the suggestions service.
    """
    return {
        "status": "ok",
        "message": "Suggestions service is operational",
        "features": [
            "mini_lesson_suggestions",
            "weak_skill_remediation",
            "tag_based_ranking"
        ]
    }

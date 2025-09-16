"""
Personalized recommendations service for students based on skill mastery and content similarity.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from ..db.models import User, Class, Lesson, Assignment, Question, Response, Submission, Enrollment
from ..services.embeddings import embed_text
from ..services.grading import cosine


def compute_skill_mastery(student_id: int, db: Session) -> Dict[str, float]:
    """
    Compute skill mastery for a student based on their response history.
    
    Args:
        student_id: ID of the student
        db: Database session
        
    Returns:
        Dictionary mapping skill_tag -> mastery score (0-1, where 1 is perfect mastery)
    """
    # Get all responses for the student with their questions and skill tags
    responses = db.query(Response, Question).join(
        Question, Response.question_id == Question.id
    ).join(
        Submission, Response.submission_id == Submission.id
    ).filter(
        Submission.student_id == student_id
    ).all()
    
    skill_scores = {}  # skill_tag -> list of scores
    
    for response, question in responses:
        if not question.skill_tags:
            continue
            
        # Determine the score to use: teacher_score if available, else ai_score
        score = response.teacher_score if response.teacher_score is not None else response.ai_score
        
        if score is None:
            continue
            
        # Normalize score to 0-1 range (assuming scores are 0-100)
        normalized_score = score / 100.0
        
        # Add this score to each skill tag for this question
        for skill_tag in question.skill_tags:
            if skill_tag not in skill_scores:
                skill_scores[skill_tag] = []
            skill_scores[skill_tag].append(normalized_score)
    
    # Compute average mastery for each skill
    skill_mastery = {}
    for skill_tag, scores in skill_scores.items():
        if scores:
            skill_mastery[skill_tag] = float(sum(scores) / len(scores))
        else:
            skill_mastery[skill_tag] = 0.0
    
    return skill_mastery


def candidate_lessons(class_id: int, db: Session, exclude_completed: bool = True) -> List[Lesson]:
    """
    Get candidate lessons for recommendations.
    
    Args:
        class_id: ID of the class
        db: Database session
        exclude_completed: Whether to exclude lessons the student has already viewed
        
    Returns:
        List of candidate lessons
    """
    query = db.query(Lesson).filter(Lesson.class_id == class_id)
    
    # TODO: Add lesson view tracking to exclude completed lessons
    # For now, we'll return all lessons in the class
    # In a full implementation, we'd join with a LessonView table
    
    return query.all()


def get_recent_lesson_embeddings(student_id: int, class_id: int, db: Session, n: int = 3) -> np.ndarray:
    """
    Get embeddings of recently viewed lessons by the student.
    
    Args:
        student_id: ID of the student
        class_id: ID of the class
        db: Database session
        n: Number of recent lessons to consider
        
    Returns:
        Mean embedding vector of recent lessons, or zero vector if none found
    """
    # TODO: Implement lesson view tracking
    # For now, we'll use a simple heuristic: get the most recent lessons in the class
    # In a full implementation, we'd track actual lesson views
    
    recent_lessons = db.query(Lesson).filter(
        Lesson.class_id == class_id
    ).order_by(
        Lesson.created_at.desc()
    ).limit(n).all()
    
    if not recent_lessons:
        # Return zero vector with the same dimension as our embeddings
        return np.zeros(384)  # all-MiniLM-L6-v2 has 384 dimensions
    
    # Get embeddings for recent lessons
    embeddings = []
    for lesson in recent_lessons:
        if lesson.embedding:
            # Convert binary embedding back to numpy array
            embedding = np.frombuffer(lesson.embedding, dtype=np.float32)
            embeddings.append(embedding)
        else:
            # Generate embedding if not stored
            try:
                embedding = embed_text(lesson.content)
                embeddings.append(embedding)
            except Exception:
                # Fallback to zero vector if embedding generation fails
                embeddings.append(np.zeros(384))
    
    if embeddings:
        # Return mean of all embeddings
        return np.mean(embeddings, axis=0)
    else:
        return np.zeros(384)


def rank_lessons_for_student(student_id: int, class_id: int, db: Session, k: int = 3) -> List[Dict]:
    """
    Rank lessons for a student based on skill mastery and content similarity.
    
    Args:
        student_id: ID of the student
        class_id: ID of the class
        db: Database session
        k: Number of recommendations to return
        
    Returns:
        List of recommendation dictionaries with lesson_id, title, reason, and score
    """
    # Get skill mastery for the student
    skill_mastery = compute_skill_mastery(student_id, db)
    
    # Get candidate lessons
    candidate_lessons_list = candidate_lessons(class_id, db, exclude_completed=True)
    
    if not candidate_lessons_list:
        return []
    
    # Get recent lesson embeddings for similarity calculation
    recent_embedding = get_recent_lesson_embeddings(student_id, class_id, db)
    
    # Score each lesson
    lesson_scores = []
    
    for lesson in candidate_lessons_list:
        if not lesson.skill_tags:
            continue
            
        # Calculate skill-based score (focus on weak skills)
        skill_scores = []
        for skill_tag in lesson.skill_tags:
            mastery = skill_mastery.get(skill_tag, 0.0)
            # Higher score for weaker skills (1 - mastery)
            skill_scores.append(1.0 - mastery)
        
        skill_score = sum(skill_scores) / len(skill_scores) if skill_scores else 0.0
        
        # Calculate content similarity score
        try:
            if lesson.embedding:
                lesson_embedding = np.frombuffer(lesson.embedding, dtype=np.float32)
            else:
                lesson_embedding = embed_text(lesson.content)
            
            # Check if embeddings are valid (not all zeros)
            if np.all(recent_embedding == 0) or np.all(lesson_embedding == 0):
                similarity_score = 0.0
            else:
                similarity_score = cosine(recent_embedding, lesson_embedding)
        except Exception:
            similarity_score = 0.0
        
        # Combined score: 60% skill weakness, 40% content similarity
        combined_score = (0.6 * skill_score) + (0.4 * similarity_score)
        
        # Generate reason
        weakest_skills = [tag for tag in lesson.skill_tags if skill_mastery.get(tag, 0.0) < 0.7]
        if weakest_skills:
            reason = f"You struggled with {', '.join(weakest_skills[:2])}; this lesson covers similar concepts."
        else:
            reason = f"This lesson covers {', '.join(lesson.skill_tags[:2])} which you're learning."
        
        lesson_scores.append({
            'lesson_id': lesson.id,
            'title': lesson.title,
            'reason': reason,
            'score': float(combined_score),
            'skill_tags': lesson.skill_tags,
            'skill_mastery': {tag: float(skill_mastery.get(tag, 0.0)) for tag in lesson.skill_tags}
        })
    
    # Sort by score (highest first) and return top k
    lesson_scores.sort(key=lambda x: x['score'], reverse=True)
    return lesson_scores[:k]


def get_student_recommendations(student_id: int, class_id: int, db: Session, k: int = 3) -> Dict:
    """
    Get personalized recommendations for a student.
    
    Args:
        student_id: ID of the student
        class_id: ID of the class
        db: Database session
        k: Number of recommendations to return
        
    Returns:
        Dictionary with recommendations and metadata
    """
    # Verify student is enrolled in the class
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.user_id == student_id,
            Enrollment.class_id == class_id
        )
    ).first()
    
    if not enrollment:
        return {
            'error': 'Student not enrolled in this class',
            'recommendations': []
        }
    
    # Get skill mastery
    skill_mastery = compute_skill_mastery(student_id, db)
    
    # Get ranked lessons
    recommendations = rank_lessons_for_student(student_id, class_id, db, k)
    
    # Get class info
    class_info = db.query(Class).filter(Class.id == class_id).first()
    
    return {
        'student_id': student_id,
        'class_id': class_id,
        'class_name': class_info.name if class_info else 'Unknown Class',
        'skill_mastery': skill_mastery,
        'recommendations': recommendations,
        'total_lessons_available': len(candidate_lessons(class_id, db, exclude_completed=False))
    }
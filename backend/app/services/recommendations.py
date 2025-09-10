from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..db.models import User, Lesson, Class, Enrollment, Submission, Response
from .embeddings import embed_text, cosine_similarity


def recommend_next_lessons(student_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Recommend next lessons for a student based on their performance and learning patterns.
    
    This is a placeholder implementation that would use:
    - Student's performance history
    - Skill gap analysis
    - Learning progression patterns
    - Content similarity analysis
    """
    
    # Get student's enrolled classes
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == student_id).all()
    class_ids = [enrollment.class_id for enrollment in enrollments]
    
    if not class_ids:
        return []
    
    # Get student's submission history
    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    
    # Analyze performance patterns
    performance_analysis = _analyze_student_performance(submissions, db)
    
    # Get available lessons
    lessons = db.query(Lesson).filter(Lesson.class_id.in_(class_ids)).all()
    
    # Score lessons based on various factors
    lesson_scores = []
    for lesson in lessons:
        score = _score_lesson_for_student(lesson, performance_analysis, db)
        lesson_scores.append((lesson, score))
    
    # Sort by score and return top recommendations
    lesson_scores.sort(key=lambda x: x[1], reverse=True)
    
    recommendations = []
    for lesson, score in lesson_scores[:3]:  # Top 3 recommendations
        class_ = db.query(Class).filter(Class.id == lesson.class_id).first()
        
        recommendation = {
            "lesson_id": lesson.id,
            "title": lesson.title,
            "content": lesson.content[:200] + "..." if len(lesson.content) > 200 else lesson.content,
            "class_name": class_.name if class_ else "Unknown Class",
            "why": _generate_recommendation_reason(lesson, performance_analysis, score),
            "skill_tags": lesson.skill_tags or [],
            "difficulty_score": _estimate_difficulty(lesson, performance_analysis),
            "relevance_score": score
        }
        recommendations.append(recommendation)
    
    return recommendations


def _analyze_student_performance(submissions: List[Submission], db: Session) -> Dict[str, Any]:
    """Analyze student's performance patterns."""
    
    if not submissions:
        return {
            "average_score": 0.7,  # Default assumption
            "weak_areas": [],
            "strong_areas": [],
            "learning_style": "balanced",
            "difficulty_preference": "medium"
        }
    
    # Calculate average scores
    total_score = 0
    score_count = 0
    
    for submission in submissions:
        if submission.ai_score is not None:
            total_score += submission.ai_score / 100.0  # Convert to 0-1 scale
            score_count += 1
        elif submission.teacher_score is not None:
            total_score += submission.teacher_score / 100.0
            score_count += 1
    
    average_score = total_score / score_count if score_count > 0 else 0.7
    
    # Analyze skill patterns (placeholder)
    weak_areas = ["algebra", "problem_solving"]  # Mock data
    strong_areas = ["reading_comprehension", "writing"]  # Mock data
    
    # Determine learning style based on performance patterns
    if average_score >= 0.8:
        learning_style = "advanced"
    elif average_score >= 0.6:
        learning_style = "balanced"
    else:
        learning_style = "needs_support"
    
    return {
        "average_score": average_score,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
        "learning_style": learning_style,
        "difficulty_preference": "medium" if average_score >= 0.6 else "easy"
    }


def _score_lesson_for_student(lesson: Lesson, performance_analysis: Dict[str, Any], db: Session) -> float:
    """Score how relevant a lesson is for a specific student."""
    
    base_score = 0.5
    
    # Factor 1: Skill alignment with weak areas
    if lesson.skill_tags:
        weak_area_bonus = sum(0.2 for tag in lesson.skill_tags if tag in performance_analysis["weak_areas"])
        base_score += weak_area_bonus
    
    # Factor 2: Difficulty appropriateness
    estimated_difficulty = _estimate_difficulty(lesson, performance_analysis)
    if performance_analysis["difficulty_preference"] == "easy" and estimated_difficulty <= 0.4:
        base_score += 0.2
    elif performance_analysis["difficulty_preference"] == "medium" and 0.3 <= estimated_difficulty <= 0.7:
        base_score += 0.2
    elif performance_analysis["difficulty_preference"] == "hard" and estimated_difficulty >= 0.6:
        base_score += 0.2
    
    # Factor 3: Learning style compatibility
    if performance_analysis["learning_style"] == "advanced" and len(lesson.content) > 500:
        base_score += 0.1
    elif performance_analysis["learning_style"] == "needs_support" and len(lesson.content) < 300:
        base_score += 0.1
    
    return min(base_score, 1.0)


def _estimate_difficulty(lesson: Lesson, performance_analysis: Dict[str, Any]) -> float:
    """Estimate the difficulty level of a lesson."""
    
    # Base difficulty from content length and complexity
    content_length = len(lesson.content)
    if content_length < 200:
        base_difficulty = 0.3
    elif content_length < 500:
        base_difficulty = 0.5
    else:
        base_difficulty = 0.7
    
    # Adjust based on skill tags
    if lesson.skill_tags:
        advanced_skills = ["calculus", "advanced_algebra", "critical_thinking", "analysis"]
        if any(skill in lesson.skill_tags for skill in advanced_skills):
            base_difficulty += 0.2
    
    return min(base_difficulty, 1.0)


def _generate_recommendation_reason(lesson: Lesson, performance_analysis: Dict[str, Any], score: float) -> str:
    """Generate a human-readable reason for the recommendation."""
    
    reasons = []
    
    # Check skill alignment
    if lesson.skill_tags and performance_analysis["weak_areas"]:
        matching_skills = [tag for tag in lesson.skill_tags if tag in performance_analysis["weak_areas"]]
        if matching_skills:
            reasons.append(f"This lesson covers {', '.join(matching_skills[:2])}, which you can strengthen.")
    
    # Check difficulty appropriateness
    estimated_difficulty = _estimate_difficulty(lesson, performance_analysis)
    if performance_analysis["learning_style"] == "advanced" and estimated_difficulty >= 0.6:
        reasons.append("This lesson provides the challenge level that matches your advanced learning pace.")
    elif performance_analysis["learning_style"] == "needs_support" and estimated_difficulty <= 0.5:
        reasons.append("This lesson is designed to build your confidence with manageable content.")
    
    # Check content relevance
    if len(lesson.content) > 400:
        reasons.append("The comprehensive content will help deepen your understanding.")
    elif len(lesson.content) < 300:
        reasons.append("The concise format makes it easy to digest and apply.")
    
    # Default reason if no specific reasons found
    if not reasons:
        reasons.append("This lesson aligns well with your current learning progress and upcoming assignments.")
    
    return " ".join(reasons[:2])  # Return top 2 reasons

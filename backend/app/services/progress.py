"""
Student progress tracking service for skill mastery analysis.
"""

import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from collections import defaultdict

from ..db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from ..core.config import settings


def get_student_skill_mastery(class_id: int, student_id: int, db: Session) -> Dict:
    """
    Calculate student mastery for each skill tag based on their responses.
    
    Args:
        class_id: ID of the class
        student_id: ID of the student
        db: Database session
        
    Returns:
        Dictionary with skill mastery data and overall average
    """
    # Get all responses for the student in this class
    responses = db.query(Response, Question, Assignment).join(
        Question, Response.question_id == Question.id
    ).join(
        Assignment, Question.assignment_id == Assignment.id
    ).filter(
        Assignment.class_id == class_id,
        Response.submission_id.in_(
            db.query(Submission.id).filter(Submission.student_id == student_id)
        )
    ).all()
    
    # Group responses by skill tag
    skill_data = defaultdict(list)
    
    for response, question, assignment in responses:
        # Parse skill tags from question
        skill_tags = []
        if question.skill_tags:
            try:
                if isinstance(question.skill_tags, str):
                    skill_tags = json.loads(question.skill_tags)
                else:
                    skill_tags = question.skill_tags
            except (json.JSONDecodeError, TypeError):
                skill_tags = []
        
        # Calculate score for this response
        score = None
        if question.type == "mcq":
            # For MCQ: 1 for correct, 0 for incorrect
            if response.teacher_score is not None:
                score = 1.0 if response.teacher_score >= 1.0 else 0.0
            elif response.ai_score is not None:
                score = 1.0 if response.ai_score >= 1.0 else 0.0
        else:  # short answer
            # For short answer: use teacher_score if present, else ai_score (0-1)
            if response.teacher_score is not None:
                score = response.teacher_score
            elif response.ai_score is not None:
                score = response.ai_score
        
        # Add score to each skill tag
        if score is not None:
            for skill_tag in skill_tags:
                skill_data[skill_tag].append({
                    'score': score,
                    'question_id': question.id,
                    'question_type': question.type,
                    'assignment_id': assignment.id,
                    'assignment_title': assignment.title
                })
    
    # Calculate mastery for each skill
    skill_mastery = []
    all_scores = []
    
    for skill_tag, responses in skill_data.items():
        if not responses:
            continue
        
        # Calculate average mastery for this skill
        scores = [r['score'] for r in responses]
        mastery = sum(scores) / len(scores)
        all_scores.extend(scores)
        
        skill_mastery.append({
            'tag': skill_tag,
            'mastery': round(mastery, 3),
            'samples': len(responses),
            'responses': responses
        })
    
    # Sort by mastery (ascending - weakest skills first)
    skill_mastery.sort(key=lambda x: x['mastery'])
    
    # Calculate overall mastery average
    overall_mastery = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    return {
        'skill_mastery': skill_mastery,
        'overall_mastery_avg': round(overall_mastery, 3),
        'total_responses': len(all_scores),
        'skills_analyzed': len(skill_mastery),
        'analysis_summary': {
            'mcq_scoring': '1.0 for correct, 0.0 for incorrect',
            'short_answer_scoring': 'teacher_score if present, else ai_score (0-1)',
            'mastery_calculation': 'average of all responses for each skill tag'
        }
    }


def get_class_skill_summary(class_id: int, db: Session) -> Dict:
    """
    Get summary of skill mastery across all students in a class.
    
    Args:
        class_id: ID of the class
        db: Database session
        
    Returns:
        Dictionary with class-wide skill mastery summary
    """
    # Get all students in the class
    students = db.query(User).join(Enrollment).filter(
        Enrollment.class_id == class_id,
        User.role == "student"
    ).all()
    
    class_skill_data = defaultdict(list)
    student_count = 0
    
    for student in students:
        student_mastery = get_student_skill_mastery(class_id, student.id, db)
        
        if student_mastery['total_responses'] > 0:
            student_count += 1
            
            # Add each skill's mastery to class data
            for skill_data in student_mastery['skill_mastery']:
                class_skill_data[skill_data['tag']].append({
                    'student_id': student.id,
                    'student_name': student.name,
                    'mastery': skill_data['mastery'],
                    'samples': skill_data['samples']
                })
    
    # Calculate class averages for each skill
    class_skill_summary = []
    for skill_tag, student_data in class_skill_data.items():
        if not student_data:
            continue
        
        masteries = [s['mastery'] for s in student_data]
        avg_mastery = sum(masteries) / len(masteries)
        
        class_skill_summary.append({
            'tag': skill_tag,
            'avg_mastery': round(avg_mastery, 3),
            'students_with_data': len(student_data),
            'total_students': student_count,
            'coverage': round(len(student_data) / student_count * 100, 1) if student_count > 0 else 0
        })
    
    # Sort by average mastery (ascending - weakest skills first)
    class_skill_summary.sort(key=lambda x: x['avg_mastery'])
    
    return {
        'class_id': class_id,
        'skill_summary': class_skill_summary,
        'total_students': student_count,
        'skills_analyzed': len(class_skill_summary)
    }

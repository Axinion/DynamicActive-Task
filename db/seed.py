#!/usr/bin/env python3
"""
Database seeding script for K12 LMS.
Run this script from the backend directory with the virtual environment activated.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Enrollment, Lesson, Assignment, Question, Submission, Response
from app.core.security import get_password_hash

def seed_database():
    """Seed the database with demo data."""
    
    # Create tables
    print("Creating database tables...")
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data (in development)
        print("Clearing existing data...")
        db.query(Response).delete()
        db.query(Submission).delete()
        db.query(Question).delete()
        db.query(Assignment).delete()
        db.query(Lesson).delete()
        db.query(Enrollment).delete()
        db.query(Class).delete()
        db.query(User).delete()
        db.commit()
        
        # Create demo users
        print("Creating demo users...")
        
        # Teacher
        teacher = User(
            email="teacher@example.com",
            name="Ms. Johnson",
            role="teacher",
            password_hash=get_password_hash("pass")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        # Student
        student = User(
            email="student@example.com",
            name="Alex Student",
            role="student",
            password_hash=get_password_hash("pass")
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        
        # Create demo class
        print("Creating demo class...")
        demo_class = Class(
            name="Algebra I",
            teacher_id=teacher.id,
            invite_code="ABC123"
        )
        db.add(demo_class)
        db.commit()
        db.refresh(demo_class)
        
        # Create enrollment
        print("Creating enrollment...")
        enrollment = Enrollment(
            user_id=student.id,
            class_id=demo_class.id
        )
        db.add(enrollment)
        db.commit()
        
        # Create demo lessons
        print("Creating demo lessons...")
        
        lesson1 = Lesson(
            class_id=demo_class.id,
            title="Introduction to Linear Equations",
            content="Linear equations are fundamental to algebra. They represent relationships between variables where the highest power of the variable is 1. In this lesson, we'll explore how to solve simple linear equations and understand their graphical representations.",
            skill_tags=["linear_equations", "algebra", "problem_solving"]
        )
        db.add(lesson1)
        
        lesson2 = Lesson(
            class_id=demo_class.id,
            title="Graphing Linear Functions",
            content="Graphing linear functions helps us visualize the relationship between variables. We'll learn about slope, y-intercept, and how to plot points to create accurate graphs of linear equations.",
            skill_tags=["graphing", "linear_functions", "slope", "visualization"]
        )
        db.add(lesson2)
        
        lesson3 = Lesson(
            class_id=demo_class.id,
            title="Systems of Linear Equations",
            content="Sometimes we need to solve multiple linear equations simultaneously. This lesson covers methods for solving systems of linear equations, including substitution and elimination methods.",
            skill_tags=["systems_of_equations", "substitution", "elimination", "advanced_algebra"]
        )
        db.add(lesson3)
        
        db.commit()
        
        # Create demo assignment
        print("Creating demo assignment...")
        assignment = Assignment(
            class_id=demo_class.id,
            title="Linear Equations Quiz",
            type="quiz",
            rubric={
                "accuracy": 40,
                "method": 30,
                "explanation": 20,
                "presentation": 10
            },
            due_at=datetime.now() + timedelta(days=7)
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create demo questions
        print("Creating demo questions...")
        
        # MCQ question
        question1 = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What is the solution to the equation 2x + 5 = 13?",
            options=["x = 4", "x = 6", "x = 8", "x = 9"],
            answer_key="x = 4",
            skill_tags=["linear_equations", "basic_algebra"]
        )
        db.add(question1)
        
        # Short answer question
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Explain the steps to solve the equation 3x - 7 = 14. Show your work and explain each step.",
            answer_key="Add 7 to both sides: 3x = 21. Then divide both sides by 3: x = 7. The key steps are isolating the variable by performing inverse operations.",
            skill_tags=["linear_equations", "problem_solving", "explanation"]
        )
        db.add(question2)
        
        db.commit()
        
        # Create demo submission
        print("Creating demo submission...")
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            ai_score=85,
            ai_explanation="Student demonstrated good understanding of linear equations. The multiple choice answer was correct, and the short answer showed proper algebraic manipulation with clear steps."
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Create demo responses
        print("Creating demo responses...")
        
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="x = 4",
            ai_score=100,
            ai_feedback="Correct! You properly solved the equation by isolating the variable."
        )
        db.add(response1)
        
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="First, I add 7 to both sides to get 3x = 21. Then I divide by 3 to get x = 7. This works because we're doing the same operation to both sides.",
            ai_score=75,
            ai_feedback="Good work! You showed the correct steps and explained the reasoning. Consider mentioning that we're using inverse operations to isolate the variable."
        )
        db.add(response2)
        
        db.commit()
        
        print("✅ Seed complete!")
        print(f"Created:")
        print(f"  - 1 teacher: {teacher.email}")
        print(f"  - 1 student: {student.email}")
        print(f"  - 1 class: {demo_class.name} (invite code: {demo_class.invite_code})")
        print(f"  - 1 enrollment")
        print(f"  - 3 lessons")
        print(f"  - 1 assignment with 2 questions")
        print(f"  - 1 submission with responses")
        print(f"\nDemo credentials:")
        print(f"  Teacher: teacher@example.com / pass")
        print(f"  Student: student@example.com / pass")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

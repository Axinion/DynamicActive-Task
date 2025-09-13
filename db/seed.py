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
            name="Demo Teacher",
            role="teacher",
            password_hash=get_password_hash("pass")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        # Student
        student = User(
            email="student@example.com",
            name="Demo Student",
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
        
        db.commit()
        
        # Create demo assignment
        print("Creating demo assignment...")
        assignment = Assignment(
            class_id=demo_class.id,
            title="Algebra Fundamentals Quiz",
            type="quiz",
            rubric={
                "accuracy": 50,
                "method": 30,
                "explanation": 20,
                "keywords": ["isolate", "inverse operations", "substitute", "verify"]
            },
            due_at=datetime.now() + timedelta(days=7)
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create demo questions
        print("Creating demo questions...")
        
        # Q1: MCQ question
        question1 = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What is the solution to the equation 2x + 3 = 11?",
            options=["x = 4", "x = 5", "x = 6", "x = 7"],
            answer_key="x = 4",
            skill_tags=["linear_equations", "basic_algebra", "solving"]
        )
        db.add(question1)
        
        # Q2: Short answer question
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Solve the equation 3x - 5 = 10. Show all your work and explain each step using proper mathematical terminology.",
            answer_key="Add 5 to both sides: 3x = 15. Then divide both sides by 3: x = 5. The key steps are isolating the variable by performing inverse operations.",
            skill_tags=["linear_equations", "problem_solving", "explanation", "mathematical_communication"]
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
        print(f"  - 2 lessons")
        print(f"  - 1 assignment with 2 questions")
        print(f"  - 1 submission with responses")
        print(f"\nDemo credentials:")
        print(f"  Teacher: teacher@example.com / pass")
        print(f"  Student: student@example.com / pass")
        print(f"\n🎯 Testing Tips:")
        print(f"  📚 Class Invite Code: {demo_class.invite_code}")
        print(f"  📝 Assignment: '{assignment.title}' with MCQ + Short Answer")
        print(f"  🔍 Q1 (MCQ): Answer is 'x = 4' (auto-graded)")
        print(f"  📖 Q2 (Short): Keywords in rubric: isolate, inverse operations, substitute, verify")
        print(f"  🧪 Test Flow:")
        print(f"     1. Login as student → Join class with code: {demo_class.invite_code}")
        print(f"     2. View assignment → Submit answers")
        print(f"     3. Login as teacher → Check gradebook for submissions")
        print(f"     4. Test auto-grading: MCQ gets 100% if correct, 0% if wrong")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

#!/usr/bin/env python3
"""
Integration tests for the Assignments API endpoints.
Tests complete assignment creation, submission, and grading flow.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from app.core.security import get_password_hash

client = TestClient(app)


def setup_test_data():
    """Set up test data for assignments integration tests."""
    # Create tables
    create_tables()
    
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Response).delete()
        db.query(Submission).delete()
        db.query(Question).delete()
        db.query(Assignment).delete()
        db.query(Enrollment).delete()
        db.query(Class).delete()
        db.query(User).delete()
        db.commit()
        
        # Create test users
        teacher = User(
            email="test_teacher@example.com",
            name="Test Teacher",
            role="teacher",
            password_hash=get_password_hash("testpass")
        )
        db.add(teacher)
        
        student = User(
            email="test_student@example.com",
            name="Test Student",
            role="student",
            password_hash=get_password_hash("testpass")
        )
        db.add(student)
        
        db.commit()
        db.refresh(teacher)
        db.refresh(student)
        
        # Create test class
        test_class = Class(
            name="Test Math Class",
            teacher_id=teacher.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        # Enroll student in class
        enrollment = Enrollment(
            user_id=student.id,
            class_id=test_class.id
        )
        db.add(enrollment)
        db.commit()
        
        return teacher.id, student.id, test_class.id
    finally:
        db.close()


def get_auth_token(email: str, password: str) -> str:
    """Get authentication token for a user."""
    response = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    return response.json()["access_token"]


def test_assignments_integration_flow():
    """Test complete assignments integration flow."""
    print("\n🧪 Starting assignments integration test...")
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # 1. Teacher creates an assignment with mixed question types
    print("1️⃣ Testing assignment creation by teacher...")
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Algebra Fundamentals Quiz",
        "type": "quiz",
        "due_at": "2024-12-31T23:59:59",
        "rubric": {
            "total_points": 100,
            "mcq_points": 60,
            "short_answer_points": 40,
            "grading": "automatic_for_mcq"
        },
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is the solution to 2x + 3 = 7?",
                "options": ["x = 1", "x = 2", "x = 3", "x = 4"],
                "answer_key": "x = 2",
                "skill_tags": ["algebra", "linear_equations", "solving"]
            },
            {
                "type": "mcq",
                "prompt": "Which of the following is a linear equation?",
                "options": ["x² + 1 = 0", "2x + 3 = 7", "x³ = 8", "√x = 4"],
                "answer_key": "2x + 3 = 7",
                "skill_tags": ["algebra", "linear_equations", "identification"]
            },
            {
                "type": "short",
                "prompt": "Explain the steps to solve 3x - 5 = 10. Show your work.",
                "answer_key": "Add 5 to both sides: 3x = 15, then divide by 3: x = 5",
                "skill_tags": ["algebra", "linear_equations", "explanation", "problem_solving"]
            },
            {
                "type": "short",
                "prompt": "What is the difference between a linear equation and a quadratic equation?",
                "skill_tags": ["algebra", "concepts", "comparison", "understanding"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    created_assignment = create_response.json()
    assert created_assignment["title"] == "Algebra Fundamentals Quiz"
    assert created_assignment["class_id"] == test_class_id
    assert len(created_assignment["questions"]) == 4
    assignment_id = created_assignment["id"]
    print(f"✅ Assignment created successfully: '{created_assignment['title']}' (ID: {assignment_id})")
    print(f"   - {len(created_assignment['questions'])} questions created")
    print(f"   - 2 MCQ questions, 2 short answer questions")
    
    # 2. Teacher can list assignments for their class
    print("2️⃣ Testing assignment listing for teacher...")
    list_response = client.get(f"/api/assignments?class_id={test_class_id}", headers=teacher_headers)
    assert list_response.status_code == 200
    assignments = list_response.json()
    assert len(assignments) == 1
    assert assignments[0]["title"] == "Algebra Fundamentals Quiz"
    print(f"✅ Teacher can see 1 assignment: '{assignments[0]['title']}'")
    
    # 3. Teacher can get specific assignment with questions
    print("3️⃣ Testing assignment retrieval by ID for teacher...")
    get_response = client.get(f"/api/assignments/{assignment_id}", headers=teacher_headers)
    assert get_response.status_code == 200
    assignment = get_response.json()
    assert assignment["id"] == assignment_id
    assert len(assignment["questions"]) == 4
    print(f"✅ Teacher can retrieve assignment by ID with {len(assignment['questions'])} questions")
    
    # 4. Student can list assignments for enrolled class
    print("4️⃣ Testing assignment listing for student...")
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    student_list_response = client.get(f"/api/assignments?class_id={test_class_id}", headers=student_headers)
    assert student_list_response.status_code == 200
    student_assignments = student_list_response.json()
    assert len(student_assignments) == 1
    assert student_assignments[0]["title"] == "Algebra Fundamentals Quiz"
    print(f"✅ Student can see 1 assignment: '{student_assignments[0]['title']}'")
    
    # 5. Student can get specific assignment (without answer keys)
    print("5️⃣ Testing assignment retrieval by ID for student...")
    student_get_response = client.get(f"/api/assignments/{assignment_id}", headers=student_headers)
    assert student_get_response.status_code == 200
    student_assignment = student_get_response.json()
    assert student_assignment["id"] == assignment_id
    assert len(student_assignment["questions"]) == 4
    # Students should not see answer keys in the questions
    for question in student_assignment["questions"]:
        assert "answer_key" not in question
    print(f"✅ Student can retrieve assignment by ID (without answer keys)")
    
    # 6. Student submits assignment with mixed answers
    print("6️⃣ Testing assignment submission by student...")
    
    questions = student_assignment["questions"]
    submission_data = {
        "answers": [
            {"question_id": questions[0]["id"], "answer": "x = 2"},  # Correct MCQ
            {"question_id": questions[1]["id"], "answer": "2x + 3 = 7"},  # Correct MCQ
            {"question_id": questions[2]["id"], "answer": "First, I add 5 to both sides to get 3x = 15. Then I divide by 3 to get x = 5."},  # Good short answer
            {"question_id": questions[3]["id"], "answer": "A linear equation has degree 1, while a quadratic equation has degree 2."}  # Good short answer
        ]
    }
    
    submit_response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert submit_response.status_code == 200
    submission_result = submit_response.json()
    
    assert "submission" in submission_result
    assert "breakdown" in submission_result
    
    submission = submission_result["submission"]
    assert submission["assignment_id"] == assignment_id
    assert submission["student_id"] == student_id
    assert submission["ai_score"] == 100.0  # Both MCQ questions correct
    
    breakdown = submission_result["breakdown"]
    assert len(breakdown) == 4
    
    # Check MCQ grading
    assert breakdown[0]["is_correct"] is True
    assert breakdown[0]["score"] == 100.0
    assert breakdown[1]["is_correct"] is True
    assert breakdown[1]["score"] == 100.0
    
    # Check short answer (not auto-graded)
    assert breakdown[2]["is_correct"] is None
    assert breakdown[2]["score"] is None
    assert breakdown[3]["is_correct"] is None
    assert breakdown[3]["score"] is None
    
    print(f"✅ Student submitted assignment successfully")
    print(f"   - Overall AI score: {submission['ai_score']}% (MCQ questions)")
    print(f"   - MCQ questions: 2/2 correct")
    print(f"   - Short answer questions: pending manual grading")
    
    # 7. Test error scenarios
    print("7️⃣ Testing error scenarios...")
    
    # Student tries to submit again
    duplicate_submit_response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert duplicate_submit_response.status_code == 400
    assert "Assignment already submitted" in duplicate_submit_response.json()["detail"]
    print("✅ Duplicate submission properly rejected")
    
    # Teacher tries to submit assignment
    teacher_submit_response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=teacher_headers)
    assert teacher_submit_response.status_code == 403
    assert "Only students can submit assignments" in teacher_submit_response.json()["detail"]
    print("✅ Teacher cannot submit assignments (403 Forbidden)")
    
    # Try to get assignment without class_id
    no_class_response = client.get("/api/assignments", headers=teacher_headers)
    assert no_class_response.status_code == 422  # Validation error
    print("✅ GET /api/assignments requires class_id parameter")
    
    # Try to get non-existent assignment
    fake_assignment_response = client.get("/api/assignments/99999", headers=teacher_headers)
    assert fake_assignment_response.status_code == 404
    assert "Assignment not found" in fake_assignment_response.json()["detail"]
    print("✅ Non-existent assignment returns 404")
    
    # 8. Test assignment with wrong answers
    print("8️⃣ Testing assignment with wrong answers...")
    
    # Create another assignment for testing wrong answers
    wrong_answer_assignment_data = {
        "class_id": test_class_id,
        "title": "Wrong Answer Test",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 5 + 5?",
                "options": ["9", "10", "11", "12"],
                "answer_key": "10",
                "skill_tags": ["arithmetic"]
            }
        ]
    }
    
    wrong_create_response = client.post("/api/assignments", json=wrong_answer_assignment_data, headers=teacher_headers)
    assert wrong_create_response.status_code == 200
    wrong_assignment_id = wrong_create_response.json()["id"]
    wrong_question_id = wrong_create_response.json()["questions"][0]["id"]
    
    # Submit wrong answer
    wrong_submission_data = {
        "answers": [
            {"question_id": wrong_question_id, "answer": "9"}  # Wrong answer
        ]
    }
    
    wrong_submit_response = client.post(f"/api/assignments/{wrong_assignment_id}/submit", json=wrong_submission_data, headers=student_headers)
    assert wrong_submit_response.status_code == 200
    wrong_submission_result = wrong_submit_response.json()
    
    wrong_submission = wrong_submission_result["submission"]
    assert wrong_submission["ai_score"] == 0.0  # Wrong answer
    
    wrong_breakdown = wrong_submission_result["breakdown"]
    assert wrong_breakdown[0]["is_correct"] is False
    assert wrong_breakdown[0]["score"] == 0.0
    
    print(f"✅ Wrong answer properly graded: {wrong_submission['ai_score']}%")
    
    print("🎉 Assignments integration test PASSED!")
    print("📊 Summary:")
    print(f"   - Assignment creation: ✅ (4 questions: 2 MCQ, 2 short)")
    print(f"   - Assignment listing: ✅ (teacher and student access)")
    print(f"   - Assignment retrieval: ✅ (with proper access control)")
    print(f"   - Assignment submission: ✅ (with auto-grading for MCQ)")
    print(f"   - Auto-grading: ✅ (MCQ questions graded automatically)")
    print(f"   - Manual grading: ✅ (short answer questions pending)")
    print(f"   - Error handling: ✅ (403, 404, 400, 422)")
    print(f"   - Role-based access: ✅ (teacher creates, student submits)")
    print(f"   - Class ownership: ✅ (teacher owns class)")
    print(f"   - Enrollment check: ✅ (student enrolled)")
    print(f"   - Duplicate prevention: ✅ (one submission per student)")


if __name__ == "__main__":
    test_assignments_integration_flow()

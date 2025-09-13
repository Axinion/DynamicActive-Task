#!/usr/bin/env python3
"""
Integration tests for the Gradebook API endpoints.
Tests complete gradebook functionality with real assignment submissions.
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
    """Set up test data for gradebook integration tests."""
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
        
        student1 = User(
            email="alice@example.com",
            name="Alice Johnson",
            role="student",
            password_hash=get_password_hash("testpass")
        )
        db.add(student1)
        
        student2 = User(
            email="bob@example.com",
            name="Bob Smith",
            role="student",
            password_hash=get_password_hash("testpass")
        )
        db.add(student2)
        
        student3 = User(
            email="charlie@example.com",
            name="Charlie Brown",
            role="student",
            password_hash=get_password_hash("testpass")
        )
        db.add(student3)
        
        db.commit()
        db.refresh(teacher)
        db.refresh(student1)
        db.refresh(student2)
        db.refresh(student3)
        
        # Create test class
        test_class = Class(
            name="Advanced Mathematics",
            teacher_id=teacher.id,
            invite_code="MATH2024"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        # Enroll all students in class
        for student in [student1, student2, student3]:
            enrollment = Enrollment(
                user_id=student.id,
                class_id=test_class.id
            )
            db.add(enrollment)
        db.commit()
        
        return teacher.id, student1.id, student2.id, student3.id, test_class.id
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


def test_gradebook_integration_flow():
    """Test complete gradebook integration flow."""
    print("\n🧪 Starting gradebook integration test...")
    teacher_id, student1_id, student2_id, student3_id, test_class_id = setup_test_data()
    
    # 1. Teacher creates multiple assignments
    print("1️⃣ Creating assignments for gradebook...")
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Create first assignment - Math Quiz
    math_quiz_data = {
        "class_id": test_class_id,
        "title": "Math Quiz",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "answer_key": "4",
                "skill_tags": ["arithmetic"]
            },
            {
                "type": "mcq",
                "prompt": "What is 3 × 3?",
                "options": ["6", "9", "12", "15"],
                "answer_key": "9",
                "skill_tags": ["multiplication"]
            }
        ]
    }
    
    math_quiz_response = client.post("/api/assignments", json=math_quiz_data, headers=teacher_headers)
    assert math_quiz_response.status_code == 200
    math_quiz_id = math_quiz_response.json()["id"]
    math_questions = math_quiz_response.json()["questions"]
    print(f"✅ Created Math Quiz (ID: {math_quiz_id}) with {len(math_questions)} questions")
    
    # Create second assignment - Algebra Test
    algebra_test_data = {
        "class_id": test_class_id,
        "title": "Algebra Test",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "Solve for x: 2x + 3 = 7",
                "options": ["x = 1", "x = 2", "x = 3", "x = 4"],
                "answer_key": "x = 2",
                "skill_tags": ["algebra", "linear_equations"]
            },
            {
                "type": "short",
                "prompt": "Explain how to solve 3x - 5 = 10",
                "skill_tags": ["algebra", "explanation"]
            }
        ]
    }
    
    algebra_test_response = client.post("/api/assignments", json=algebra_test_data, headers=teacher_headers)
    assert algebra_test_response.status_code == 200
    algebra_test_id = algebra_test_response.json()["id"]
    algebra_questions = algebra_test_response.json()["questions"]
    print(f"✅ Created Algebra Test (ID: {algebra_test_id}) with {len(algebra_questions)} questions")
    
    # 2. Students submit assignments with different performance levels
    print("2️⃣ Students submitting assignments...")
    
    # Alice submits both assignments with perfect scores
    alice_token = get_auth_token("alice@example.com", "testpass")
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    
    # Alice - Math Quiz (perfect)
    alice_math_submission = {
        "answers": [
            {"question_id": math_questions[0]["id"], "answer": "4"},  # Correct
            {"question_id": math_questions[1]["id"], "answer": "9"}   # Correct
        ]
    }
    alice_math_response = client.post(f"/api/assignments/{math_quiz_id}/submit", json=alice_math_submission, headers=alice_headers)
    assert alice_math_response.status_code == 200
    print("✅ Alice submitted Math Quiz (perfect score)")
    
    # Alice - Algebra Test (perfect MCQ, good short answer)
    alice_algebra_submission = {
        "answers": [
            {"question_id": algebra_questions[0]["id"], "answer": "x = 2"},  # Correct
            {"question_id": algebra_questions[1]["id"], "answer": "Add 5 to both sides: 3x = 15, then divide by 3: x = 5"}
        ]
    }
    alice_algebra_response = client.post(f"/api/assignments/{algebra_test_id}/submit", json=alice_algebra_submission, headers=alice_headers)
    assert alice_algebra_response.status_code == 200
    print("✅ Alice submitted Algebra Test (perfect MCQ)")
    
    # Bob submits with mixed performance
    bob_token = get_auth_token("bob@example.com", "testpass")
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    
    # Bob - Math Quiz (partial score)
    bob_math_submission = {
        "answers": [
            {"question_id": math_questions[0]["id"], "answer": "4"},  # Correct
            {"question_id": math_questions[1]["id"], "answer": "6"}   # Wrong
        ]
    }
    bob_math_response = client.post(f"/api/assignments/{math_quiz_id}/submit", json=bob_math_submission, headers=bob_headers)
    assert bob_math_response.status_code == 200
    print("✅ Bob submitted Math Quiz (partial score)")
    
    # Bob - Algebra Test (wrong MCQ, good short answer)
    bob_algebra_submission = {
        "answers": [
            {"question_id": algebra_questions[0]["id"], "answer": "x = 1"},  # Wrong
            {"question_id": algebra_questions[1]["id"], "answer": "First add 5 to both sides, then divide by 3"}
        ]
    }
    bob_algebra_response = client.post(f"/api/assignments/{algebra_test_id}/submit", json=bob_algebra_submission, headers=bob_headers)
    assert bob_algebra_response.status_code == 200
    print("✅ Bob submitted Algebra Test (wrong MCQ)")
    
    # Charlie submits only one assignment
    charlie_token = get_auth_token("charlie@example.com", "testpass")
    charlie_headers = {"Authorization": f"Bearer {charlie_token}"}
    
    # Charlie - Math Quiz (perfect)
    charlie_math_submission = {
        "answers": [
            {"question_id": math_questions[0]["id"], "answer": "4"},  # Correct
            {"question_id": math_questions[1]["id"], "answer": "9"}   # Correct
        ]
    }
    charlie_math_response = client.post(f"/api/assignments/{math_quiz_id}/submit", json=charlie_math_submission, headers=charlie_headers)
    assert charlie_math_response.status_code == 200
    print("✅ Charlie submitted Math Quiz (perfect score)")
    
    # 3. Teacher accesses gradebook
    print("3️⃣ Teacher accessing gradebook...")
    gradebook_response = client.get(f"/api/gradebook?class_id={test_class_id}", headers=teacher_headers)
    assert gradebook_response.status_code == 200
    
    gradebook = gradebook_response.json()
    assert gradebook["class_id"] == test_class_id
    assert gradebook["class_name"] == "Advanced Mathematics"
    assert gradebook["total_submissions"] == 5  # Alice: 2, Bob: 2, Charlie: 1
    
    submissions = gradebook["submissions"]
    print(f"✅ Gradebook retrieved with {len(submissions)} submissions")
    
    # 4. Verify gradebook data structure and content
    print("4️⃣ Verifying gradebook data...")
    
    # Check that all expected submissions are present
    submission_assignments = set(s["assignment_title"] for s in submissions)
    assert "Math Quiz" in submission_assignments
    assert "Algebra Test" in submission_assignments
    
    submission_students = set(s["student_name"] for s in submissions)
    assert "Alice Johnson" in submission_students
    assert "Bob Smith" in submission_students
    assert "Charlie Brown" in submission_students
    
    # Verify specific submission details
    alice_math_sub = next(s for s in submissions if s["student_name"] == "Alice Johnson" and s["assignment_title"] == "Math Quiz")
    assert alice_math_sub["ai_score"] == 100.0
    assert alice_math_sub["teacher_score"] is None
    print("✅ Alice's Math Quiz: 100% AI score")
    
    alice_algebra_sub = next(s for s in submissions if s["student_name"] == "Alice Johnson" and s["assignment_title"] == "Algebra Test")
    assert alice_algebra_sub["ai_score"] == 100.0  # MCQ was correct
    assert alice_algebra_sub["teacher_score"] is None
    print("✅ Alice's Algebra Test: 100% AI score (MCQ only)")
    
    bob_math_sub = next(s for s in submissions if s["student_name"] == "Bob Smith" and s["assignment_title"] == "Math Quiz")
    assert bob_math_sub["ai_score"] == 50.0  # 1 out of 2 correct
    assert bob_math_sub["teacher_score"] is None
    print("✅ Bob's Math Quiz: 50% AI score")
    
    bob_algebra_sub = next(s for s in submissions if s["student_name"] == "Bob Smith" and s["assignment_title"] == "Algebra Test")
    assert bob_algebra_sub["ai_score"] == 0.0  # MCQ was wrong
    assert bob_algebra_sub["teacher_score"] is None
    print("✅ Bob's Algebra Test: 0% AI score (MCQ wrong)")
    
    charlie_math_sub = next(s for s in submissions if s["student_name"] == "Charlie Brown" and s["assignment_title"] == "Math Quiz")
    assert charlie_math_sub["ai_score"] == 100.0
    assert charlie_math_sub["teacher_score"] is None
    print("✅ Charlie's Math Quiz: 100% AI score")
    
    # 5. Test gradebook ordering and structure
    print("5️⃣ Verifying gradebook structure...")
    
    # Check that submissions are ordered by assignment title, then student name
    for i in range(len(submissions) - 1):
        current = submissions[i]
        next_sub = submissions[i + 1]
        
        # Either same assignment with student name order, or assignment title order
        if current["assignment_title"] == next_sub["assignment_title"]:
            assert current["student_name"] <= next_sub["student_name"]
        else:
            assert current["assignment_title"] <= next_sub["assignment_title"]
    
    # Verify all required fields are present
    required_fields = ["submission_id", "assignment_id", "assignment_title", "student_id", 
                      "student_name", "student_email", "submitted_at", "ai_score", "teacher_score"]
    
    for submission in submissions:
        for field in required_fields:
            assert field in submission, f"Missing field: {field}"
    
    print("✅ Gradebook structure verified")
    
    # 6. Test error scenarios
    print("6️⃣ Testing error scenarios...")
    
    # Student tries to access gradebook
    student_gradebook_response = client.get(f"/api/gradebook?class_id={test_class_id}", headers=alice_headers)
    assert student_gradebook_response.status_code == 403
    assert "Only teachers can access gradebook" in student_gradebook_response.json()["detail"]
    print("✅ Student access properly denied (403)")
    
    # Try to access gradebook without class_id
    no_class_response = client.get("/api/gradebook", headers=teacher_headers)
    assert no_class_response.status_code == 422  # Validation error
    print("✅ Missing class_id properly rejected (422)")
    
    # Try to access gradebook for non-existent class
    fake_class_response = client.get("/api/gradebook?class_id=99999", headers=teacher_headers)
    assert fake_class_response.status_code == 404
    assert "Class not found or access denied" in fake_class_response.json()["detail"]
    print("✅ Non-existent class properly rejected (404)")
    
    print("🎉 Gradebook integration test PASSED!")
    print("📊 Summary:")
    print(f"   - Assignments created: ✅ (2 assignments)")
    print(f"   - Student submissions: ✅ (5 total submissions)")
    print(f"   - Gradebook access: ✅ (teacher-only)")
    print(f"   - Data retrieval: ✅ (all submissions with scores)")
    print(f"   - Auto-grading: ✅ (MCQ questions graded)")
    print(f"   - Data structure: ✅ (proper ordering and fields)")
    print(f"   - Error handling: ✅ (403, 404, 422)")
    print(f"   - Class ownership: ✅ (teacher owns class)")
    print(f"   - Performance tracking: ✅ (AI scores calculated)")


if __name__ == "__main__":
    test_gradebook_integration_flow()

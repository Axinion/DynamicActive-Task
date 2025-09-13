#!/usr/bin/env python3
"""
Tests for the Gradebook API endpoints.
Tests gradebook access and data retrieval functionality.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from app.core.security import get_password_hash

client = TestClient(app)


def setup_test_data():
    """Set up test data for gradebook tests."""
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
            email="test_student1@example.com",
            name="Test Student 1",
            role="student",
            password_hash=get_password_hash("testpass")
        )
        db.add(student1)
        
        student2 = User(
            email="test_student2@example.com",
            name="Test Student 2",
            role="student",
            password_hash=get_password_hash("testpass")
        )
        db.add(student2)
        
        db.commit()
        db.refresh(teacher)
        db.refresh(student1)
        db.refresh(student2)
        
        # Create test class
        test_class = Class(
            name="Test Math Class",
            teacher_id=teacher.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        # Enroll students in class
        enrollment1 = Enrollment(
            user_id=student1.id,
            class_id=test_class.id
        )
        db.add(enrollment1)
        
        enrollment2 = Enrollment(
            user_id=student2.id,
            class_id=test_class.id
        )
        db.add(enrollment2)
        db.commit()
        
        return teacher.id, student1.id, student2.id, test_class.id
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


def create_test_assignment_and_submissions(teacher_id, student1_id, student2_id, test_class_id):
    """Create a test assignment and submissions for gradebook testing."""
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Create assignment
    assignment_data = {
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
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    question_id = create_response.json()["questions"][0]["id"]
    
    # Student 1 submits correct answer
    student1_token = get_auth_token("test_student1@example.com", "testpass")
    student1_headers = {"Authorization": f"Bearer {student1_token}"}
    
    submission1_data = {
        "answers": [
            {"question_id": question_id, "answer": "4"}  # Correct
        ]
    }
    
    submit1_response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission1_data, headers=student1_headers)
    assert submit1_response.status_code == 200
    
    # Student 2 submits wrong answer
    student2_token = get_auth_token("test_student2@example.com", "testpass")
    student2_headers = {"Authorization": f"Bearer {student2_token}"}
    
    submission2_data = {
        "answers": [
            {"question_id": question_id, "answer": "3"}  # Wrong
        ]
    }
    
    submit2_response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission2_data, headers=student2_headers)
    assert submit2_response.status_code == 200
    
    return assignment_id


def test_gradebook_teacher_only():
    """Test that only teachers can access gradebook."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    # Student tries to access gradebook
    student_token = get_auth_token("test_student1@example.com", "testpass")
    headers = {"Authorization": f"Bearer {student_token}"}
    
    response = client.get(f"/api/gradebook?class_id={test_class_id}", headers=headers)
    assert response.status_code == 403
    assert "Only teachers can access gradebook" in response.json()["detail"]


def test_gradebook_teacher_owns_class():
    """Test that teachers can only access gradebook for classes they own."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    # Create another teacher and class
    db = SessionLocal()
    try:
        other_teacher = User(
            email="other_teacher@example.com",
            name="Other Teacher",
            role="teacher",
            password_hash=get_password_hash("testpass")
        )
        db.add(other_teacher)
        db.commit()
        db.refresh(other_teacher)
        
        other_class = Class(
            name="Other Class",
            teacher_id=other_teacher.id,
            invite_code="OTHER1"
        )
        db.add(other_class)
        db.commit()
        db.refresh(other_class)
        other_class_id = other_class.id
    finally:
        db.close()
    
    # First teacher tries to access other teacher's class gradebook
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.get(f"/api/gradebook?class_id={other_class_id}", headers=headers)
    assert response.status_code == 404
    assert "Class not found or access denied" in response.json()["detail"]


def test_gradebook_requires_class_id():
    """Test that GET /api/gradebook requires class_id parameter."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Try to get gradebook without class_id
    response = client.get("/api/gradebook", headers=headers)
    assert response.status_code == 422  # Validation error


def test_gradebook_empty_class():
    """Test gradebook for class with no assignments or submissions."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.get(f"/api/gradebook?class_id={test_class_id}", headers=headers)
    assert response.status_code == 200
    
    gradebook = response.json()
    assert gradebook["class_id"] == test_class_id
    assert gradebook["class_name"] == "Test Math Class"
    assert gradebook["total_submissions"] == 0
    assert gradebook["submissions"] == []


def test_gradebook_with_submissions():
    """Test gradebook with assignments and submissions."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    # Create assignment and submissions
    assignment_id = create_test_assignment_and_submissions(teacher_id, student1_id, student2_id, test_class_id)
    
    # Teacher accesses gradebook
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.get(f"/api/gradebook?class_id={test_class_id}", headers=headers)
    assert response.status_code == 200
    
    gradebook = response.json()
    assert gradebook["class_id"] == test_class_id
    assert gradebook["class_name"] == "Test Math Class"
    assert gradebook["total_submissions"] == 2
    assert len(gradebook["submissions"]) == 2
    
    # Check submission details
    submissions = gradebook["submissions"]
    
    # Find student 1's submission (correct answer)
    student1_submission = next(s for s in submissions if s["student_name"] == "Test Student 1")
    assert student1_submission["assignment_id"] == assignment_id
    assert student1_submission["assignment_title"] == "Math Quiz"
    assert student1_submission["student_id"] == student1_id
    assert student1_submission["ai_score"] == 100.0
    assert student1_submission["teacher_score"] is None
    
    # Find student 2's submission (wrong answer)
    student2_submission = next(s for s in submissions if s["student_name"] == "Test Student 2")
    assert student2_submission["assignment_id"] == assignment_id
    assert student2_submission["assignment_title"] == "Math Quiz"
    assert student2_submission["student_id"] == student2_id
    assert student2_submission["ai_score"] == 0.0
    assert student2_submission["teacher_score"] is None


def test_gradebook_multiple_assignments():
    """Test gradebook with multiple assignments."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    # Create first assignment and submissions
    assignment1_id = create_test_assignment_and_submissions(teacher_id, student1_id, student2_id, test_class_id)
    
    # Create second assignment
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment2_data = {
        "class_id": test_class_id,
        "title": "Algebra Quiz",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 3 + 3?",
                "options": ["5", "6", "7", "8"],
                "answer_key": "6",
                "skill_tags": ["arithmetic"]
            }
        ]
    }
    
    create2_response = client.post("/api/assignments", json=assignment2_data, headers=teacher_headers)
    assert create2_response.status_code == 200
    assignment2_id = create2_response.json()["id"]
    question2_id = create2_response.json()["questions"][0]["id"]
    
    # Student 1 submits second assignment
    student1_token = get_auth_token("test_student1@example.com", "testpass")
    student1_headers = {"Authorization": f"Bearer {student1_token}"}
    
    submission2_data = {
        "answers": [
            {"question_id": question2_id, "answer": "6"}  # Correct
        ]
    }
    
    submit2_response = client.post(f"/api/assignments/{assignment2_id}/submit", json=submission2_data, headers=student1_headers)
    assert submit2_response.status_code == 200
    
    # Teacher accesses gradebook
    response = client.get(f"/api/gradebook?class_id={test_class_id}", headers=teacher_headers)
    assert response.status_code == 200
    
    gradebook = response.json()
    assert gradebook["total_submissions"] == 3  # 2 from first assignment, 1 from second
    
    submissions = gradebook["submissions"]
    
    # Check that submissions are ordered by assignment title, then student name
    assert len(submissions) == 3
    
    # Verify all submissions are present
    assignment_titles = [s["assignment_title"] for s in submissions]
    assert "Algebra Quiz" in assignment_titles
    assert "Math Quiz" in assignment_titles
    
    student_names = [s["student_name"] for s in submissions]
    assert "Test Student 1" in student_names
    assert "Test Student 2" in student_names


def test_gradebook_nonexistent_class():
    """Test gradebook for non-existent class."""
    teacher_id, student1_id, student2_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.get("/api/gradebook?class_id=99999", headers=headers)
    assert response.status_code == 404
    assert "Class not found or access denied" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

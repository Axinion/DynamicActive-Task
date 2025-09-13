#!/usr/bin/env python3
"""
Tests for the Assignments API endpoints.
Tests assignment creation, question management, and submission functionality.
"""

import sys
import os
import pytest
import json
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from app.core.security import get_password_hash

client = TestClient(app)


def setup_test_data():
    """Set up test data for assignments tests."""
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


def test_create_assignment_teacher_only():
    """Test that only teachers can create assignments."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Student tries to create an assignment
    student_token = get_auth_token("test_student@example.com", "testpass")
    headers = {"Authorization": f"Bearer {student_token}"}
    
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
    
    response = client.post("/api/assignments", json=assignment_data, headers=headers)
    assert response.status_code == 403
    assert "Only teachers can create assignments" in response.json()["detail"]


def test_create_assignment_teacher_owns_class():
    """Test that teachers can only create assignments for classes they own."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
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
    
    # First teacher tries to create assignment in other teacher's class
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": other_class_id,
        "title": "Unauthorized Assignment",
        "type": "quiz",
        "questions": []
    }
    
    response = client.post("/api/assignments", json=assignment_data, headers=headers)
    assert response.status_code == 404
    assert "Class not found or access denied" in response.json()["detail"]


def test_create_assignment_success():
    """Test successful assignment creation by teacher."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Algebra Quiz",
        "type": "quiz",
        "due_at": "2024-12-31T23:59:59",
        "rubric": {"points": 100, "grading": "automatic"},
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "answer_key": "4",
                "skill_tags": ["arithmetic", "addition"]
            },
            {
                "type": "short",
                "prompt": "Explain how to solve 2x + 3 = 7",
                "answer_key": "x = 2",
                "skill_tags": ["algebra", "equations"]
            }
        ]
    }
    
    response = client.post("/api/assignments", json=assignment_data, headers=headers)
    assert response.status_code == 200
    
    created_assignment = response.json()
    assert created_assignment["title"] == "Algebra Quiz"
    assert created_assignment["class_id"] == test_class_id
    assert created_assignment["type"] == "quiz"
    assert len(created_assignment["questions"]) == 2
    assert created_assignment["questions"][0]["type"] == "mcq"
    assert created_assignment["questions"][1]["type"] == "short"
    assert created_assignment["id"] is not None


def test_get_assignments_requires_class_id():
    """Test that GET /api/assignments requires class_id parameter."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Try to get assignments without class_id
    response = client.get("/api/assignments", headers=headers)
    assert response.status_code == 422  # Validation error


def test_get_assignments_teacher_access():
    """Test that teachers can get assignments from their classes."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Test Assignment",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "Test question?",
                "options": ["A", "B", "C", "D"],
                "answer_key": "A",
                "skill_tags": ["test"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=headers)
    assert create_response.status_code == 200
    
    # Get assignments
    response = client.get(f"/api/assignments?class_id={test_class_id}", headers=headers)
    assert response.status_code == 200
    
    assignments = response.json()
    assert len(assignments) == 1
    assert assignments[0]["title"] == "Test Assignment"


def test_get_assignments_student_access():
    """Test that students can get assignments from classes they're enrolled in."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Student Assignment",
        "type": "written",
        "questions": [
            {
                "type": "short",
                "prompt": "Write an essay about math",
                "skill_tags": ["writing", "math"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    
    # Student gets assignments
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    response = client.get(f"/api/assignments?class_id={test_class_id}", headers=student_headers)
    assert response.status_code == 200
    
    assignments = response.json()
    assert len(assignments) == 1
    assert assignments[0]["title"] == "Student Assignment"


def test_get_assignment_by_id():
    """Test getting a specific assignment by ID."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Specific Assignment",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 1 + 1?",
                "options": ["1", "2", "3", "4"],
                "answer_key": "2",
                "skill_tags": ["arithmetic"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    
    # Get the specific assignment
    response = client.get(f"/api/assignments/{assignment_id}", headers=headers)
    assert response.status_code == 200
    
    assignment = response.json()
    assert assignment["id"] == assignment_id
    assert assignment["title"] == "Specific Assignment"
    assert len(assignment["questions"]) == 1


def test_submit_assignment_student_only():
    """Test that only students can submit assignments."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Submission Test",
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
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    
    # Teacher tries to submit assignment
    submission_data = {
        "answers": [
            {"question_id": create_response.json()["questions"][0]["id"], "answer": "6"}
        ]
    }
    
    response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=teacher_headers)
    assert response.status_code == 403
    assert "Only students can submit assignments" in response.json()["detail"]


def test_submit_assignment_success():
    """Test successful assignment submission by student."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Submission Success Test",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 4 + 4?",
                "options": ["7", "8", "9", "10"],
                "answer_key": "8",
                "skill_tags": ["arithmetic"]
            },
            {
                "type": "short",
                "prompt": "Explain addition",
                "skill_tags": ["explanation"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    questions = create_response.json()["questions"]
    
    # Student submits assignment
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    submission_data = {
        "answers": [
            {"question_id": questions[0]["id"], "answer": "8"},  # Correct MCQ answer
            {"question_id": questions[1]["id"], "answer": "Addition is combining numbers"}  # Short answer
        ]
    }
    
    response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert response.status_code == 200
    
    submission_response = response.json()
    assert "submission" in submission_response
    assert "breakdown" in submission_response
    
    submission = submission_response["submission"]
    assert submission["assignment_id"] == assignment_id
    assert submission["student_id"] == student_id
    assert submission["ai_score"] == 100.0  # MCQ was correct
    
    breakdown = submission_response["breakdown"]
    assert len(breakdown) == 2
    assert breakdown[0]["is_correct"] is True  # MCQ correct
    assert breakdown[0]["score"] == 100.0
    assert breakdown[1]["is_correct"] is None  # Short answer not auto-graded
    assert breakdown[1]["score"] is None


def test_submit_assignment_wrong_answer():
    """Test assignment submission with wrong MCQ answer."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
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
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    question_id = create_response.json()["questions"][0]["id"]
    
    # Student submits wrong answer
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    submission_data = {
        "answers": [
            {"question_id": question_id, "answer": "9"}  # Wrong answer
        ]
    }
    
    response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert response.status_code == 200
    
    submission_response = response.json()
    submission = submission_response["submission"]
    assert submission["ai_score"] == 0.0  # Wrong answer
    
    breakdown = submission_response["breakdown"]
    assert breakdown[0]["is_correct"] is False
    assert breakdown[0]["score"] == 0.0


def test_submit_assignment_already_submitted():
    """Test that students cannot submit the same assignment twice."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create an assignment first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": test_class_id,
        "title": "Duplicate Submission Test",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 1 + 1?",
                "options": ["1", "2", "3", "4"],
                "answer_key": "2",
                "skill_tags": ["arithmetic"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    question_id = create_response.json()["questions"][0]["id"]
    
    # Student submits assignment
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    submission_data = {
        "answers": [
            {"question_id": question_id, "answer": "2"}
        ]
    }
    
    # First submission
    response1 = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert response1.status_code == 200
    
    # Second submission (should fail)
    response2 = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert response2.status_code == 400
    assert "Assignment already submitted" in response2.json()["detail"]


def test_submit_assignment_not_enrolled():
    """Test that students cannot submit assignments for classes they're not enrolled in."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create another class that student is not enrolled in
    db = SessionLocal()
    try:
        other_class = Class(
            name="Other Class",
            teacher_id=teacher_id,
            invite_code="OTHER2"
        )
        db.add(other_class)
        db.commit()
        db.refresh(other_class)
        other_class_id = other_class.id
    finally:
        db.close()
    
    # Create assignment in other class
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    assignment_data = {
        "class_id": other_class_id,
        "title": "Unauthorized Assignment",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "Unauthorized question?",
                "options": ["A", "B", "C", "D"],
                "answer_key": "A",
                "skill_tags": ["unauthorized"]
            }
        ]
    }
    
    create_response = client.post("/api/assignments", json=assignment_data, headers=teacher_headers)
    assert create_response.status_code == 200
    assignment_id = create_response.json()["id"]
    question_id = create_response.json()["questions"][0]["id"]
    
    # Student tries to submit assignment from class they're not enrolled in
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    submission_data = {
        "answers": [
            {"question_id": question_id, "answer": "A"}
        ]
    }
    
    response = client.post(f"/api/assignments/{assignment_id}/submit", json=submission_data, headers=student_headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

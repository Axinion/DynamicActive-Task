#!/usr/bin/env python3
"""
Tests for the Lessons API endpoints.
Tests lesson creation, listing, and retrieval functionality.
"""

import sys
import os
import pytest
import httpx
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Lesson, Enrollment
from app.core.security import get_password_hash

client = TestClient(app)


def setup_test_data():
    """Set up test data for lessons tests."""
    # Create tables
    create_tables()
    
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Lesson).delete()
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
        
        # Return IDs instead of objects to avoid session issues
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


def test_create_lesson_teacher_only():
    """Test that only teachers can create lessons."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Student tries to create a lesson
    student_token = get_auth_token("test_student@example.com", "testpass")
    headers = {"Authorization": f"Bearer {student_token}"}
    
    lesson_data = {
        "class_id": test_class_id,
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts...",
        "skill_tags": ["algebra", "equations", "variables"]
    }
    
    response = client.post("/api/lessons", json=lesson_data, headers=headers)
    assert response.status_code == 403
    assert "Only teachers can create lessons" in response.json()["detail"]


def test_create_lesson_teacher_owns_class():
    """Test that teachers can only create lessons for classes they own."""
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
    
    # First teacher tries to create lesson in other teacher's class
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    lesson_data = {
        "class_id": other_class_id,
        "title": "Unauthorized Lesson",
        "content": "This should not be allowed...",
        "skill_tags": ["unauthorized"]
    }
    
    response = client.post("/api/lessons", json=lesson_data, headers=headers)
    assert response.status_code == 404
    assert "Class not found or access denied" in response.json()["detail"]


def test_create_lesson_success():
    """Test successful lesson creation by teacher."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    lesson_data = {
        "class_id": test_class_id,
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts including variables, equations, and solving for x.",
        "skill_tags": ["algebra", "equations", "variables"]
    }
    
    response = client.post("/api/lessons", json=lesson_data, headers=headers)
    assert response.status_code == 200
    
    created_lesson = response.json()
    assert created_lesson["title"] == "Introduction to Algebra"
    assert created_lesson["class_id"] == test_class_id
    assert created_lesson["skill_tags"] == ["algebra", "equations", "variables"]
    assert "created_at" in created_lesson
    assert created_lesson["id"] is not None


def test_get_lessons_requires_class_id():
    """Test that GET /api/lessons requires class_id parameter."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Try to get lessons without class_id
    response = client.get("/api/lessons", headers=headers)
    assert response.status_code == 422  # Validation error


def test_get_lessons_teacher_access():
    """Test that teachers can get lessons from their classes."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create a lesson first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    lesson_data = {
        "class_id": test_class_id,
        "title": "Test Lesson",
        "content": "Test content",
        "skill_tags": ["test"]
    }
    
    create_response = client.post("/api/lessons", json=lesson_data, headers=headers)
    assert create_response.status_code == 200
    
    # Get lessons
    response = client.get(f"/api/lessons?class_id={test_class_id}", headers=headers)
    assert response.status_code == 200
    
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["title"] == "Test Lesson"
    assert lessons[0]["class_name"] == "Test Math Class"


def test_get_lessons_student_access():
    """Test that students can get lessons from classes they're enrolled in."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create a lesson first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    lesson_data = {
        "class_id": test_class_id,
        "title": "Student Lesson",
        "content": "Content for students",
        "skill_tags": ["student", "learning"]
    }
    
    create_response = client.post("/api/lessons", json=lesson_data, headers=teacher_headers)
    assert create_response.status_code == 200
    
    # Student gets lessons
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    response = client.get(f"/api/lessons?class_id={test_class_id}", headers=student_headers)
    assert response.status_code == 200
    
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["title"] == "Student Lesson"


def test_get_lessons_student_not_enrolled():
    """Test that students cannot get lessons from classes they're not enrolled in."""
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
    
    # Student tries to get lessons from class they're not enrolled in
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    response = client.get(f"/api/lessons?class_id={other_class_id}", headers=student_headers)
    assert response.status_code == 200  # Returns empty list, not error
    assert response.json() == []


def test_get_lesson_by_id():
    """Test getting a specific lesson by ID."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create a lesson
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    lesson_data = {
        "class_id": test_class_id,
        "title": "Specific Lesson",
        "content": "Specific lesson content",
        "skill_tags": ["specific"]
    }
    
    create_response = client.post("/api/lessons", json=lesson_data, headers=headers)
    assert create_response.status_code == 200
    lesson_id = create_response.json()["id"]
    
    # Get the specific lesson
    response = client.get(f"/api/lessons/{lesson_id}", headers=headers)
    assert response.status_code == 200
    
    lesson = response.json()
    assert lesson["id"] == lesson_id
    assert lesson["title"] == "Specific Lesson"
    assert lesson["class_name"] == "Test Math Class"


def test_get_lesson_access_denied():
    """Test that users cannot access lessons from classes they don't have access to."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # Create another teacher and class
    db = SessionLocal()
    try:
        other_teacher = User(
            email="other_teacher2@example.com",
            name="Other Teacher 2",
            role="teacher",
            password_hash=get_password_hash("testpass")
        )
        db.add(other_teacher)
        db.commit()
        db.refresh(other_teacher)
        
        other_class = Class(
            name="Private Class",
            teacher_id=other_teacher.id,
            invite_code="PRIVATE"
        )
        db.add(other_class)
        db.commit()
        db.refresh(other_class)
        
        # Create lesson in other teacher's class
        other_lesson = Lesson(
            class_id=other_class.id,
            title="Private Lesson",
            content="Private content",
            skill_tags=["private"]
        )
        db.add(other_lesson)
        db.commit()
        db.refresh(other_lesson)
        other_lesson_id = other_lesson.id
    finally:
        db.close()
    
    # First teacher tries to access other teacher's lesson
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.get(f"/api/lessons/{other_lesson_id}", headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_lessons_sorted_by_created_at_desc():
    """Test that lessons are returned sorted by created_at DESC."""
    teacher_id, student_id, test_class_id = setup_test_data()
    
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Create multiple lessons
    lesson1_data = {
        "class_id": test_class_id,
        "title": "First Lesson",
        "content": "First lesson content",
        "skill_tags": ["first"]
    }
    
    lesson2_data = {
        "class_id": test_class_id,
        "title": "Second Lesson",
        "content": "Second lesson content",
        "skill_tags": ["second"]
    }
    
    # Create lessons with a longer delay to ensure different timestamps
    response1 = client.post("/api/lessons", json=lesson1_data, headers=headers)
    assert response1.status_code == 200
    
    import time
    time.sleep(1)  # Longer delay to ensure different timestamps
    
    response2 = client.post("/api/lessons", json=lesson2_data, headers=headers)
    assert response2.status_code == 200
    
    # Get lessons and verify order
    response = client.get(f"/api/lessons?class_id={test_class_id}", headers=headers)
    assert response.status_code == 200
    
    lessons = response.json()
    assert len(lessons) == 2
    
    # Check that lessons are sorted by created_at DESC
    # The second lesson should come first (most recent)
    lesson1_created = lessons[0]['created_at']
    lesson2_created = lessons[1]['created_at']
    
    # With a 1-second delay, timestamps should be different
    assert lesson1_created > lesson2_created, f"Expected {lesson1_created} > {lesson2_created}"
    
    # Verify the correct lessons are in the right order
    assert lessons[0]['title'] == "Second Lesson"
    assert lessons[1]['title'] == "First Lesson"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

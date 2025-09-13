#!/usr/bin/env python3
"""
Tests for the Classes API endpoints.
Tests class creation, listing, and joining functionality.
"""

import sys
import os
import pytest
import httpx
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Enrollment
from app.core.security import get_password_hash

client = TestClient(app)


def setup_test_data():
    """Set up test data for classes tests."""
    # Create tables
    create_tables()
    
    db = SessionLocal()
    try:
        # Clear existing data
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
        
        return teacher, student
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


def test_class_creation_and_joining_flow():
    """Test the complete flow: teacher creates class, student joins."""
    # Setup test data
    teacher, student = setup_test_data()
    
    # Get auth tokens
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    student_token = get_auth_token("test_student@example.com", "testpass")
    
    # Test 1: Teacher creates a class
    headers = {"Authorization": f"Bearer {teacher_token}"}
    class_data = {"name": "Test Math Class"}
    
    response = client.post("/api/classes", json=class_data, headers=headers)
    assert response.status_code == 200
    
    created_class = response.json()
    assert created_class["name"] == "Test Math Class"
    assert created_class["teacher_id"] == teacher.id
    assert "invite_code" in created_class
    assert len(created_class["invite_code"]) == 7  # Should be 7 characters
    
    invite_code = created_class["invite_code"]
    class_id = created_class["id"]
    
    # Test 2: Teacher can list their classes
    response = client.get("/api/classes", headers=headers)
    assert response.status_code == 200
    
    classes = response.json()
    assert len(classes) == 1
    assert classes[0]["name"] == "Test Math Class"
    assert classes[0]["student_count"] == 0  # No students yet
    
    # Test 3: Student cannot see classes before joining
    student_headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/api/classes", headers=student_headers)
    assert response.status_code == 200
    
    student_classes = response.json()
    assert len(student_classes) == 0  # No classes yet
    
    # Test 4: Student joins the class using invite code
    join_data = {"invite_code": invite_code}
    response = client.post("/api/classes/join", json=join_data, headers=student_headers)
    assert response.status_code == 200
    
    join_response = response.json()
    assert join_response["success"] is True
    assert join_response["class_id"] == class_id
    assert "Successfully joined class" in join_response["message"]
    
    # Test 5: Student can now see the class they joined
    response = client.get("/api/classes", headers=student_headers)
    assert response.status_code == 200
    
    student_classes = response.json()
    assert len(student_classes) == 1
    assert student_classes[0]["name"] == "Test Math Class"
    
    # Test 6: Teacher can see updated student count
    response = client.get("/api/classes", headers=headers)
    assert response.status_code == 200
    
    classes = response.json()
    assert len(classes) == 1
    assert classes[0]["student_count"] == 1  # One student now
    
    # Test 7: Student cannot join the same class twice
    response = client.post("/api/classes/join", json=join_data, headers=student_headers)
    assert response.status_code == 200
    
    join_response = response.json()
    assert join_response["success"] is False
    assert "Already enrolled" in join_response["message"]


def test_class_creation_teacher_only():
    """Test that only teachers can create classes."""
    teacher, student = setup_test_data()
    
    # Student tries to create a class
    student_token = get_auth_token("test_student@example.com", "testpass")
    headers = {"Authorization": f"Bearer {student_token}"}
    
    response = client.post("/api/classes", json={"name": "Unauthorized Class"}, headers=headers)
    assert response.status_code == 403
    assert "Only teachers can create classes" in response.json()["detail"]


def test_class_joining_student_only():
    """Test that only students can join classes."""
    teacher, student = setup_test_data()
    
    # Create a class first
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.post("/api/classes", json={"name": "Test Class"}, headers=headers)
    assert response.status_code == 200
    invite_code = response.json()["invite_code"]
    
    # Teacher tries to join their own class
    join_data = {"invite_code": invite_code}
    response = client.post("/api/classes/join", json=join_data, headers=headers)
    assert response.status_code == 403
    assert "Only students can join classes" in response.json()["detail"]


def test_invalid_invite_code():
    """Test joining with invalid invite code."""
    teacher, student = setup_test_data()
    
    student_token = get_auth_token("test_student@example.com", "testpass")
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Try to join with invalid invite code
    join_data = {"invite_code": "INVALID"}
    response = client.post("/api/classes/join", json=join_data, headers=headers)
    assert response.status_code == 200
    
    join_response = response.json()
    assert join_response["success"] is False
    assert "Invalid invite code" in join_response["message"]


def test_invite_code_regeneration():
    """Test invite code regeneration by teacher."""
    teacher, student = setup_test_data()
    
    # Create a class
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.post("/api/classes", json={"name": "Test Class"}, headers=headers)
    assert response.status_code == 200
    original_invite_code = response.json()["invite_code"]
    class_id = response.json()["id"]
    
    # Regenerate invite code
    response = client.post(f"/api/classes/{class_id}/invite", headers=headers)
    assert response.status_code == 200
    
    regenerate_response = response.json()
    assert regenerate_response["success"] is True
    assert regenerate_response["invite_code"] != original_invite_code
    assert len(regenerate_response["invite_code"]) == 7
    
    # Verify the new invite code works
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    join_data = {"invite_code": regenerate_response["invite_code"]}
    response = client.post("/api/classes/join", json=join_data, headers=student_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_invite_code():
    """Test getting invite code for a class."""
    teacher, student = setup_test_data()
    
    # Create a class
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    response = client.post("/api/classes", json={"name": "Test Class"}, headers=headers)
    assert response.status_code == 200
    class_id = response.json()["id"]
    original_invite_code = response.json()["invite_code"]
    
    # Get invite code
    response = client.get(f"/api/classes/{class_id}/invite", headers=headers)
    assert response.status_code == 200
    
    invite_response = response.json()
    assert invite_response["invite_code"] == original_invite_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

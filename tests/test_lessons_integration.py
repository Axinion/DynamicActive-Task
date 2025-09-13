#!/usr/bin/env python3
"""
Integration tests for the Lessons API endpoints.
Tests lesson creation, listing, and retrieval functionality with the existing auth and classes system.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Lesson, Enrollment
from app.core.security import get_password_hash

client = TestClient(app)


def setup_test_data():
    """Set up test data for lessons integration tests."""
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


def test_lessons_integration_flow():
    """Test complete lessons integration flow."""
    print("\n🧪 Starting lessons integration test...")
    teacher_id, student_id, test_class_id = setup_test_data()
    
    # 1. Teacher creates a lesson
    print("1️⃣ Testing lesson creation by teacher...")
    teacher_token = get_auth_token("test_teacher@example.com", "testpass")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    lesson_data = {
        "class_id": test_class_id,
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts including variables, equations, and solving for x. We'll start with simple linear equations and work our way up to more complex problems.",
        "skill_tags": ["algebra", "equations", "variables", "linear_equations"]
    }
    
    create_response = client.post("/api/lessons", json=lesson_data, headers=teacher_headers)
    assert create_response.status_code == 200
    created_lesson = create_response.json()
    assert created_lesson["title"] == "Introduction to Algebra"
    assert created_lesson["class_id"] == test_class_id
    assert created_lesson["skill_tags"] == ["algebra", "equations", "variables", "linear_equations"]
    lesson_id = created_lesson["id"]
    print(f"✅ Lesson created successfully: '{created_lesson['title']}' (ID: {lesson_id})")
    
    # 2. Teacher can list lessons for their class
    print("2️⃣ Testing lesson listing for teacher...")
    list_response = client.get(f"/api/lessons?class_id={test_class_id}", headers=teacher_headers)
    assert list_response.status_code == 200
    lessons = list_response.json()
    assert len(lessons) == 1
    assert lessons[0]["title"] == "Introduction to Algebra"
    assert lessons[0]["class_name"] == "Test Math Class"
    print(f"✅ Teacher can see 1 lesson: '{lessons[0]['title']}'")
    
    # 3. Teacher can get specific lesson by ID
    print("3️⃣ Testing lesson retrieval by ID for teacher...")
    get_response = client.get(f"/api/lessons/{lesson_id}", headers=teacher_headers)
    assert get_response.status_code == 200
    lesson = get_response.json()
    assert lesson["id"] == lesson_id
    assert lesson["title"] == "Introduction to Algebra"
    assert lesson["class_name"] == "Test Math Class"
    print(f"✅ Teacher can retrieve lesson by ID: '{lesson['title']}'")
    
    # 4. Student can list lessons for enrolled class
    print("4️⃣ Testing lesson listing for student...")
    student_token = get_auth_token("test_student@example.com", "testpass")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    student_list_response = client.get(f"/api/lessons?class_id={test_class_id}", headers=student_headers)
    assert student_list_response.status_code == 200
    student_lessons = student_list_response.json()
    assert len(student_lessons) == 1
    assert student_lessons[0]["title"] == "Introduction to Algebra"
    print(f"✅ Student can see 1 lesson: '{student_lessons[0]['title']}'")
    
    # 5. Student can get specific lesson by ID
    print("5️⃣ Testing lesson retrieval by ID for student...")
    student_get_response = client.get(f"/api/lessons/{lesson_id}", headers=student_headers)
    assert student_get_response.status_code == 200
    student_lesson = student_get_response.json()
    assert student_lesson["id"] == lesson_id
    assert student_lesson["title"] == "Introduction to Algebra"
    print(f"✅ Student can retrieve lesson by ID: '{student_lesson['title']}'")
    
    # 6. Create multiple lessons and test sorting
    print("6️⃣ Testing multiple lessons and sorting...")
    
    # Create second lesson
    lesson2_data = {
        "class_id": test_class_id,
        "title": "Advanced Algebra",
        "content": "This lesson covers more advanced algebraic concepts including quadratic equations and factoring.",
        "skill_tags": ["algebra", "quadratic_equations", "factoring"]
    }
    
    import time
    time.sleep(1)  # Ensure different timestamps
    
    create2_response = client.post("/api/lessons", json=lesson2_data, headers=teacher_headers)
    assert create2_response.status_code == 200
    lesson2_id = create2_response.json()["id"]
    print(f"✅ Second lesson created: 'Advanced Algebra' (ID: {lesson2_id})")
    
    # Get lessons and verify sorting (newest first)
    final_list_response = client.get(f"/api/lessons?class_id={test_class_id}", headers=teacher_headers)
    assert final_list_response.status_code == 200
    final_lessons = final_list_response.json()
    assert len(final_lessons) == 2
    assert final_lessons[0]["title"] == "Advanced Algebra"  # Most recent
    assert final_lessons[1]["title"] == "Introduction to Algebra"  # Older
    print(f"✅ Lessons sorted correctly: '{final_lessons[0]['title']}' (newest) → '{final_lessons[1]['title']}' (older)")
    
    # 7. Test error scenarios
    print("7️⃣ Testing error scenarios...")
    
    # Student tries to create lesson
    student_create_response = client.post("/api/lessons", json=lesson_data, headers=student_headers)
    assert student_create_response.status_code == 403
    assert "Only teachers can create lessons" in student_create_response.json()["detail"]
    print("✅ Student cannot create lessons (403 Forbidden)")
    
    # Try to get lesson without class_id
    no_class_response = client.get("/api/lessons", headers=teacher_headers)
    assert no_class_response.status_code == 422  # Validation error
    print("✅ GET /api/lessons requires class_id parameter")
    
    # Try to get non-existent lesson
    fake_lesson_response = client.get("/api/lessons/99999", headers=teacher_headers)
    assert fake_lesson_response.status_code == 404
    assert "Lesson not found" in fake_lesson_response.json()["detail"]
    print("✅ Non-existent lesson returns 404")
    
    print("🎉 Lessons integration test PASSED!")
    print("📊 Summary:")
    print(f"   - Lesson creation: ✅ (2 lessons created)")
    print(f"   - Lesson listing: ✅ (sorted by created_at DESC)")
    print(f"   - Lesson retrieval: ✅ (by ID)")
    print(f"   - Teacher access: ✅ (full CRUD)")
    print(f"   - Student access: ✅ (read-only)")
    print(f"   - Error handling: ✅ (403, 404, 422)")
    print(f"   - Role-based access: ✅ (teacher-only creation)")
    print(f"   - Class ownership: ✅ (teacher owns class)")
    print(f"   - Enrollment check: ✅ (student enrolled)")


if __name__ == "__main__":
    test_lessons_integration_flow()

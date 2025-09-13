#!/usr/bin/env python3
"""
Comprehensive smoke test for the complete auth and classes flow.
Tests the end-to-end user journey: teacher login → create class → student login → join class → list classes.
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


def setup_test_database():
    """Set up a clean test database with demo users."""
    # Create tables
    create_tables()
    
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Enrollment).delete()
        db.query(Class).delete()
        db.query(User).delete()
        db.commit()
        
        # Create demo users (matching the seeded data)
        teacher = User(
            email="teacher@example.com",
            name="Demo Teacher",
            role="teacher",
            password_hash=get_password_hash("pass")
        )
        db.add(teacher)
        
        student = User(
            email="student@example.com",
            name="Demo Student",
            role="student",
            password_hash=get_password_hash("pass")
        )
        db.add(student)
        
        db.commit()
        db.refresh(teacher)
        db.refresh(student)
        
        return teacher, student
    finally:
        db.close()


def test_complete_auth_and_classes_flow():
    """
    Complete end-to-end smoke test:
    1. Teacher logs in → POST /auth/login
    2. Teacher creates class → POST /classes → capture invite code
    3. Student logs in → POST /auth/login
    4. Student joins class → POST /classes/join with invite code
    5. Student lists classes → GET /classes and assert 1 enrolled
    """
    # Setup clean test database
    teacher, student = setup_test_database()
    
    print("🧪 Starting comprehensive auth and classes flow test...")
    
    # Step 1: Teacher logs in
    print("1️⃣ Testing teacher login...")
    teacher_login_response = client.post("/api/auth/login", json={
        "email": "teacher@example.com",
        "password": "pass"
    })
    assert teacher_login_response.status_code == 200, f"Teacher login failed: {teacher_login_response.text}"
    
    teacher_data = teacher_login_response.json()
    assert "access_token" in teacher_data, "No access token in teacher login response"
    assert teacher_data["user"]["email"] == "teacher@example.com"
    assert teacher_data["user"]["role"] == "teacher"
    assert teacher_data["token_type"] == "bearer"
    
    teacher_token = teacher_data["access_token"]
    print(f"✅ Teacher logged in successfully, token: {teacher_token[:20]}...")
    
    # Step 2: Teacher creates a class
    print("2️⃣ Testing class creation...")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    class_data = {"name": "Advanced Mathematics"}
    
    create_class_response = client.post("/api/classes", json=class_data, headers=teacher_headers)
    assert create_class_response.status_code == 200, f"Class creation failed: {create_class_response.text}"
    
    created_class = create_class_response.json()
    assert created_class["name"] == "Advanced Mathematics"
    assert created_class["teacher_id"] == teacher.id
    assert "invite_code" in created_class
    assert len(created_class["invite_code"]) >= 6, "Invite code too short"
    assert len(created_class["invite_code"]) <= 8, "Invite code too long"
    
    invite_code = created_class["invite_code"]
    class_id = created_class["id"]
    print(f"✅ Class created successfully: '{created_class['name']}' with invite code: {invite_code}")
    
    # Step 3: Student logs in
    print("3️⃣ Testing student login...")
    student_login_response = client.post("/api/auth/login", json={
        "email": "student@example.com",
        "password": "pass"
    })
    assert student_login_response.status_code == 200, f"Student login failed: {student_login_response.text}"
    
    student_data = student_login_response.json()
    assert "access_token" in student_data, "No access token in student login response"
    assert student_data["user"]["email"] == "student@example.com"
    assert student_data["user"]["role"] == "student"
    assert student_data["token_type"] == "bearer"
    
    student_token = student_data["access_token"]
    print(f"✅ Student logged in successfully, token: {student_token[:20]}...")
    
    # Step 4: Student joins the class
    print("4️⃣ Testing class joining...")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    join_data = {"invite_code": invite_code}
    
    join_class_response = client.post("/api/classes/join", json=join_data, headers=student_headers)
    assert join_class_response.status_code == 200, f"Class joining failed: {join_class_response.text}"
    
    join_result = join_class_response.json()
    assert join_result["success"] is True, f"Join was not successful: {join_result}"
    assert join_result["class_id"] == class_id
    assert "Successfully joined class" in join_result["message"]
    print(f"✅ Student successfully joined class with invite code: {invite_code}")
    
    # Step 5: Student lists classes and verifies enrollment
    print("5️⃣ Testing class listing for student...")
    list_classes_response = client.get("/api/classes", headers=student_headers)
    assert list_classes_response.status_code == 200, f"Class listing failed: {list_classes_response.text}"
    
    student_classes = list_classes_response.json()
    assert len(student_classes) == 1, f"Expected 1 class, got {len(student_classes)}"
    assert student_classes[0]["name"] == "Advanced Mathematics"
    assert student_classes[0]["id"] == class_id
    print(f"✅ Student can see 1 enrolled class: '{student_classes[0]['name']}'")
    
    # Bonus: Verify teacher can see updated student count
    print("6️⃣ Testing teacher class listing with student count...")
    teacher_list_response = client.get("/api/classes", headers=teacher_headers)
    assert teacher_list_response.status_code == 200, f"Teacher class listing failed: {teacher_list_response.text}"
    
    teacher_classes = teacher_list_response.json()
    assert len(teacher_classes) == 1, f"Expected 1 class for teacher, got {len(teacher_classes)}"
    assert teacher_classes[0]["name"] == "Advanced Mathematics"
    assert teacher_classes[0]["student_count"] == 1, f"Expected 1 student, got {teacher_classes[0]['student_count']}"
    print(f"✅ Teacher can see class with 1 student enrolled")
    
    # Bonus: Test /auth/me endpoints
    print("7️⃣ Testing /auth/me endpoints...")
    
    # Teacher /auth/me
    teacher_me_response = client.get("/api/auth/me", headers=teacher_headers)
    assert teacher_me_response.status_code == 200, f"Teacher /auth/me failed: {teacher_me_response.text}"
    teacher_me_data = teacher_me_response.json()
    assert teacher_me_data["email"] == "teacher@example.com"
    assert teacher_me_data["role"] == "teacher"
    
    # Student /auth/me
    student_me_response = client.get("/api/auth/me", headers=student_headers)
    assert student_me_response.status_code == 200, f"Student /auth/me failed: {student_me_response.text}"
    student_me_data = student_me_response.json()
    assert student_me_data["email"] == "student@example.com"
    assert student_me_data["role"] == "student"
    
    print("✅ Both /auth/me endpoints working correctly")
    
    print("🎉 Complete auth and classes flow test PASSED!")
    print(f"📊 Summary:")
    print(f"   - Teacher login: ✅")
    print(f"   - Class creation: ✅ (invite code: {invite_code})")
    print(f"   - Student login: ✅")
    print(f"   - Class joining: ✅")
    print(f"   - Class listing: ✅ (1 class enrolled)")
    print(f"   - Student count: ✅ (1 student)")
    print(f"   - Auth verification: ✅")


def test_error_scenarios():
    """Test various error scenarios to ensure robust error handling."""
    print("\n🧪 Testing error scenarios...")
    
    # Setup test database
    teacher, student = setup_test_database()
    
    # Test invalid login credentials
    print("1️⃣ Testing invalid login credentials...")
    invalid_login_response = client.post("/api/auth/login", json={
        "email": "teacher@example.com",
        "password": "wrongpassword"
    })
    assert invalid_login_response.status_code == 401, "Should return 401 for invalid credentials"
    print("✅ Invalid credentials properly rejected")
    
    # Test unauthorized class creation
    print("2️⃣ Testing unauthorized class creation...")
    student_token = client.post("/api/auth/login", json={
        "email": "student@example.com",
        "password": "pass"
    }).json()["access_token"]
    
    student_headers = {"Authorization": f"Bearer {student_token}"}
    unauthorized_create_response = client.post("/api/classes", json={"name": "Unauthorized Class"}, headers=student_headers)
    assert unauthorized_create_response.status_code == 403, "Students should not be able to create classes"
    print("✅ Unauthorized class creation properly rejected")
    
    # Test invalid invite code
    print("3️⃣ Testing invalid invite code...")
    invalid_join_response = client.post("/api/classes/join", json={"invite_code": "INVALID123"}, headers=student_headers)
    assert invalid_join_response.status_code == 200, "Should return 200 but with error in response"
    join_result = invalid_join_response.json()
    assert join_result["success"] is False, "Join should fail with invalid code"
    assert "Invalid invite code" in join_result["message"]
    print("✅ Invalid invite code properly rejected")
    
    print("✅ All error scenarios handled correctly")


if __name__ == "__main__":
    print("🚀 Running comprehensive auth and classes flow smoke tests...")
    print("=" * 60)
    
    # Run the main flow test
    test_complete_auth_and_classes_flow()
    
    # Run error scenario tests
    test_error_scenarios()
    
    print("=" * 60)
    print("🎉 All smoke tests completed successfully!")
    print("\n📋 Test Summary:")
    print("✅ Complete auth and classes flow")
    print("✅ Error handling scenarios")
    print("✅ JWT authentication")
    print("✅ Role-based access control")
    print("✅ Class creation and joining")
    print("✅ Data persistence and retrieval")
    
    print("\n🚀 The K12 LMS backend is ready for development!")

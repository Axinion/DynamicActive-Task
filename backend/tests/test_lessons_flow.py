"""
Test the complete lessons flow:
1. Teacher creates a lesson
2. Student lists lessons for the class
3. Student fetches the specific lesson
"""

import pytest
import httpx
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Class, Enrollment, Lesson
from app.core.security import get_password_hash


@pytest.fixture
def setup_test_data(db: Session):
    """Set up test data: teacher, student, class, and enrollment"""
    # Create teacher
    teacher = User(
        email="teacher@test.com",
        password_hash=get_password_hash("password"),
        role="teacher",
        name="Test Teacher"
    )
    db.add(teacher)
    db.flush()
    
    # Create student
    student = User(
        email="student@test.com",
        password_hash=get_password_hash("password"),
        role="student",
        name="Test Student"
    )
    db.add(student)
    db.flush()
    
    # Create class
    test_class = Class(
        name="Test Class",
        teacher_id=teacher.id,
        invite_code="TEST123"
    )
    db.add(test_class)
    db.flush()
    
    # Create enrollment
    enrollment = Enrollment(
        class_id=test_class.id,
        user_id=student.id
    )
    db.add(enrollment)
    db.commit()
    
    return {
        "teacher_id": teacher.id,
        "student_id": student.id,
        "class_id": test_class.id
    }


def test_lessons_flow(client: httpx.Client, setup_test_data):
    """Test complete lessons flow: teacher creates lesson, student accesses it"""
    teacher_id = setup_test_data["teacher_id"]
    student_id = setup_test_data["student_id"]
    class_id = setup_test_data["class_id"]
    
    # Step 1: Teacher logs in
    teacher_login_response = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    assert teacher_login_response.status_code == 200
    teacher_token = teacher_login_response.json()["access_token"]
    
    # Step 2: Teacher creates a lesson
    lesson_data = {
        "class_id": class_id,
        "title": "Introduction to Python",
        "content": "Python is a high-level programming language known for its simplicity and readability. In this lesson, we'll cover the basics of Python syntax, variables, and data types.",
        "skill_tags": ["programming", "python", "basics", "syntax"]
    }
    
    create_lesson_response = client.post(
        "/api/lessons",
        json=lesson_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert create_lesson_response.status_code == 200
    
    created_lesson = create_lesson_response.json()
    assert created_lesson["title"] == "Introduction to Python"
    assert created_lesson["class_id"] == class_id
    assert created_lesson["content"] == lesson_data["content"]
    assert created_lesson["skill_tags"] == lesson_data["skill_tags"]
    assert "id" in created_lesson
    assert "created_at" in created_lesson
    
    lesson_id = created_lesson["id"]
    
    # Step 3: Student logs in
    student_login_response = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password"
    })
    assert student_login_response.status_code == 200
    student_token = student_login_response.json()["access_token"]
    
    # Step 4: Student lists lessons for the class
    list_lessons_response = client.get(
        f"/api/lessons?class_id={class_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert list_lessons_response.status_code == 200
    
    lessons_list = list_lessons_response.json()
    assert len(lessons_list) == 1
    assert lessons_list[0]["id"] == lesson_id
    assert lessons_list[0]["title"] == "Introduction to Python"
    assert lessons_list[0]["class_id"] == class_id
    
    # Step 5: Student fetches the specific lesson
    get_lesson_response = client.get(
        f"/api/lessons/{lesson_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert get_lesson_response.status_code == 200
    
    lesson_detail = get_lesson_response.json()
    assert lesson_detail["id"] == lesson_id
    assert lesson_detail["title"] == "Introduction to Python"
    assert lesson_detail["content"] == lesson_data["content"]
    assert lesson_detail["skill_tags"] == lesson_data["skill_tags"]
    assert lesson_detail["class_id"] == class_id
    assert "created_at" in lesson_detail


def test_teacher_can_list_own_lessons(client: httpx.Client, setup_test_data):
    """Test that teacher can list lessons they created"""
    teacher_id = setup_test_data["teacher_id"]
    class_id = setup_test_data["class_id"]
    
    # Teacher logs in
    teacher_login_response = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    assert teacher_login_response.status_code == 200
    teacher_token = teacher_login_response.json()["access_token"]
    
    # Teacher creates a lesson
    lesson_data = {
        "class_id": class_id,
        "title": "Advanced Python Concepts",
        "content": "This lesson covers advanced Python concepts including decorators, generators, and context managers.",
        "skill_tags": ["programming", "python", "advanced", "decorators"]
    }
    
    create_response = client.post(
        "/api/lessons",
        json=lesson_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert create_response.status_code == 200
    lesson_id = create_response.json()["id"]
    
    # Teacher lists lessons for the class
    list_response = client.get(
        f"/api/lessons?class_id={class_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert list_response.status_code == 200
    
    lessons = list_response.json()
    assert len(lessons) == 1
    assert lessons[0]["id"] == lesson_id
    assert lessons[0]["title"] == "Advanced Python Concepts"


def test_student_cannot_create_lessons(client: httpx.Client, setup_test_data):
    """Test that students cannot create lessons"""
    class_id = setup_test_data["class_id"]
    
    # Student logs in
    student_login_response = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password"
    })
    assert student_login_response.status_code == 200
    student_token = student_login_response.json()["access_token"]
    
    # Student tries to create a lesson
    lesson_data = {
        "class_id": class_id,
        "title": "Student Lesson",
        "content": "This should not be allowed.",
        "skill_tags": ["unauthorized"]
    }
    
    create_response = client.post(
        "/api/lessons",
        json=lesson_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert create_response.status_code == 403


def test_teacher_cannot_access_other_teacher_lessons(client: httpx.Client, db: Session):
    """Test that teachers cannot access lessons from classes they don't own"""
    # Create two teachers
    teacher1 = User(
        email="teacher1@test.com",
        password_hash=get_password_hash("password"),
        role="teacher",
        name="Teacher 1"
    )
    teacher2 = User(
        email="teacher2@test.com",
        password_hash=get_password_hash("password"),
        role="teacher",
        name="Teacher 2"
    )
    db.add_all([teacher1, teacher2])
    db.flush()
    
    # Create class for teacher1
    class1 = Class(
        name="Teacher 1 Class",
        teacher_id=teacher1.id,
        invite_code="CLASS1"
    )
    db.add(class1)
    db.flush()
    
    # Create lesson for teacher1's class
    lesson = Lesson(
        class_id=class1.id,
        title="Teacher 1 Lesson",
        content="This is teacher 1's lesson",
        skill_tags=["private"]
    )
    db.add(lesson)
    db.commit()
    
    # Teacher2 logs in
    teacher2_login = client.post("/api/auth/login", json={
        "email": "teacher2@test.com",
        "password": "password"
    })
    assert teacher2_login.status_code == 200
    teacher2_token = teacher2_login.json()["access_token"]
    
    # Teacher2 tries to access teacher1's lesson
    access_response = client.get(
        f"/api/lessons/{lesson.id}",
        headers={"Authorization": f"Bearer {teacher2_token}"}
    )
    assert access_response.status_code == 403


def test_lesson_creation_validation(client: httpx.Client, setup_test_data):
    """Test lesson creation validation"""
    class_id = setup_test_data["class_id"]
    
    # Teacher logs in
    teacher_login = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    assert teacher_login.status_code == 200
    teacher_token = teacher_login.json()["access_token"]
    
    # Test missing required fields (missing title)
    invalid_lesson = {
        "class_id": class_id,
        "content": "Some content"
        # Missing title field
    }
    
    response = client.post(
        "/api/lessons",
        json=invalid_lesson,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 422  # Validation error
    
    # Test missing content field
    invalid_lesson2 = {
        "class_id": class_id,
        "title": "Valid Title"
        # Missing content field
    }
    
    response2 = client.post(
        "/api/lessons",
        json=invalid_lesson2,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response2.status_code == 422  # Validation error

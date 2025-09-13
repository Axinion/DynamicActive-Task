"""
Test the complete assignments flow:
1. Teacher creates assignment with 1 MCQ + 1 short answer question
2. Student submits the assignment
3. Verify MCQ auto-grading and short answer storage
4. Verify submission returns overall ai_score for MCQ questions only
"""

import pytest
import httpx
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Class, Enrollment, Assignment, Question, Submission, Response
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


def test_assignments_flow(client: httpx.Client, setup_test_data):
    """Test complete assignments flow: teacher creates assignment, student submits"""
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
    
    # Step 2: Teacher creates assignment with MCQ + Short Answer questions
    assignment_data = {
        "class_id": class_id,
        "title": "Python Basics Quiz",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is the correct way to create a list in Python?",
                "options": ["list()", "[]", "new list()", "List()"],
                "answer_key": "[]",
                "skill_tags": ["python", "lists", "syntax"]
            },
            {
                "type": "short",
                "prompt": "Explain the difference between a list and a tuple in Python.",
                "skill_tags": ["python", "data-structures", "lists", "tuples"]
            }
        ]
    }
    
    create_assignment_response = client.post(
        "/api/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert create_assignment_response.status_code == 200
    
    created_assignment = create_assignment_response.json()
    assert created_assignment["title"] == "Python Basics Quiz"
    assert created_assignment["type"] == "quiz"
    assert created_assignment["class_id"] == class_id
    assert len(created_assignment["questions"]) == 2
    
    # Verify questions were created correctly
    mcq_question = created_assignment["questions"][0]
    short_question = created_assignment["questions"][1]
    
    assert mcq_question["type"] == "mcq"
    assert mcq_question["prompt"] == "What is the correct way to create a list in Python?"
    assert mcq_question["options"] == ["list()", "[]", "new list()", "List()"]
    # Note: answer_key is not included in QuestionReadLite schema
    
    assert short_question["type"] == "short"
    assert short_question["prompt"] == "Explain the difference between a list and a tuple in Python."
    
    assignment_id = created_assignment["id"]
    mcq_question_id = mcq_question["id"]
    short_question_id = short_question["id"]
    
    # Step 3: Student logs in
    student_login_response = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password"
    })
    assert student_login_response.status_code == 200
    student_token = student_login_response.json()["access_token"]
    
    # Step 4: Student submits assignment with correct MCQ answer and short answer
    submission_data = {
        "answers": [
            {
                "question_id": mcq_question_id,
                "answer": "[]"  # Correct answer
            },
            {
                "question_id": short_question_id,
                "answer": "A list is mutable and can be changed after creation, while a tuple is immutable and cannot be modified once created."
            }
        ]
    }
    
    submit_response = client.post(
        f"/api/assignments/{assignment_id}/submit",
        json=submission_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert submit_response.status_code == 200
    
    submission_result = submit_response.json()
    
    # Verify submission structure
    assert "submission" in submission_result
    assert "breakdown" in submission_result
    
    submission = submission_result["submission"]
    assert submission["assignment_id"] == assignment_id
    assert submission["student_id"] == student_id
    assert "submitted_at" in submission
    assert "id" in submission
    
    # Step 5: Verify MCQ auto-grading
    assert submission["ai_score"] is not None
    assert submission["ai_score"] == 100.0  # 1 correct MCQ out of 1 MCQ = 100%
    
    # Verify breakdown shows correct MCQ grading
    breakdown = submission_result["breakdown"]
    assert len(breakdown) == 2
    
    # Find MCQ and short answer breakdowns
    mcq_breakdown = next(b for b in breakdown if b["question_id"] == mcq_question_id)
    short_breakdown = next(b for b in breakdown if b["question_id"] == short_question_id)
    
    # MCQ should be marked as correct
    assert mcq_breakdown["is_correct"] is True
    assert mcq_breakdown["score"] == 100.0
    
    # Short answer should have null score (not auto-graded)
    assert short_breakdown["score"] is None
    assert short_breakdown["is_correct"] is None


def test_mcq_incorrect_answer(client: httpx.Client, setup_test_data):
    """Test MCQ auto-grading with incorrect answer"""
    teacher_id = setup_test_data["teacher_id"]
    student_id = setup_test_data["student_id"]
    class_id = setup_test_data["class_id"]
    
    # Teacher logs in and creates assignment
    teacher_login = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    teacher_token = teacher_login.json()["access_token"]
    
    assignment_data = {
        "class_id": class_id,
        "title": "Simple MCQ Test",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "answer_key": "4",
                "skill_tags": ["math", "addition"]
            }
        ]
    }
    
    create_response = client.post(
        "/api/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assignment_id = create_response.json()["id"]
    question_id = create_response.json()["questions"][0]["id"]
    
    # Student logs in and submits incorrect answer
    student_login = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password"
    })
    student_token = student_login.json()["access_token"]
    
    submission_data = {
        "answers": [
            {
                "question_id": question_id,
                "answer": "3"  # Incorrect answer
            }
        ]
    }
    
    submit_response = client.post(
        f"/api/assignments/{assignment_id}/submit",
        json=submission_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert submit_response.status_code == 200
    
    submission_result = submit_response.json()
    
    # Verify incorrect MCQ grading
    submission = submission_result["submission"]
    assert submission["ai_score"] == 0.0  # 0 correct MCQ out of 1 MCQ = 0%
    
    breakdown = submission_result["breakdown"]
    mcq_breakdown = breakdown[0]
    assert mcq_breakdown["is_correct"] is False
    assert mcq_breakdown["score"] == 0.0


def test_mixed_questions_scoring(client: httpx.Client, setup_test_data):
    """Test scoring with multiple MCQ and short answer questions"""
    teacher_id = setup_test_data["teacher_id"]
    student_id = setup_test_data["student_id"]
    class_id = setup_test_data["class_id"]
    
    # Teacher logs in and creates assignment
    teacher_login = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    teacher_token = teacher_login.json()["access_token"]
    
    assignment_data = {
        "class_id": class_id,
        "title": "Mixed Questions Test",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "What is 1 + 1?",
                "options": ["1", "2", "3", "4"],
                "answer_key": "2",
                "skill_tags": ["math"]
            },
            {
                "type": "mcq",
                "prompt": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "answer_key": "4",
                "skill_tags": ["math"]
            },
            {
                "type": "short",
                "prompt": "Explain what Python is.",
                "skill_tags": ["programming", "python"]
            }
        ]
    }
    
    create_response = client.post(
        "/api/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assignment_id = create_response.json()["id"]
    questions = create_response.json()["questions"]
    
    # Student logs in and submits (1 correct MCQ, 1 incorrect MCQ, 1 short answer)
    student_login = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password"
    })
    student_token = student_login.json()["access_token"]
    
    submission_data = {
        "answers": [
            {
                "question_id": questions[0]["id"],
                "answer": "2"  # Correct
            },
            {
                "question_id": questions[1]["id"],
                "answer": "3"  # Incorrect
            },
            {
                "question_id": questions[2]["id"],
                "answer": "Python is a programming language."
            }
        ]
    }
    
    submit_response = client.post(
        f"/api/assignments/{assignment_id}/submit",
        json=submission_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert submit_response.status_code == 200
    
    submission_result = submit_response.json()
    
    # Verify scoring: 1 correct MCQ out of 2 MCQ = 50%
    submission = submission_result["submission"]
    assert submission["ai_score"] == 50.0
    
    breakdown = submission_result["breakdown"]
    assert len(breakdown) == 3
    
    # First MCQ (correct)
    assert breakdown[0]["is_correct"] is True
    assert breakdown[0]["score"] == 100.0
    
    # Second MCQ (incorrect)
    assert breakdown[1]["is_correct"] is False
    assert breakdown[1]["score"] == 0.0
    
    # Short answer (not auto-graded)
    assert breakdown[2]["score"] is None
    assert breakdown[2]["is_correct"] is None


def test_student_cannot_create_assignments(client: httpx.Client, setup_test_data):
    """Test that students cannot create assignments"""
    class_id = setup_test_data["class_id"]
    
    # Student logs in
    student_login = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password"
    })
    student_token = student_login.json()["access_token"]
    
    # Student tries to create assignment
    assignment_data = {
        "class_id": class_id,
        "title": "Student Assignment",
        "type": "quiz",
        "questions": []
    }
    
    response = client.post(
        "/api/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403


def test_teacher_cannot_submit_assignments(client: httpx.Client, setup_test_data):
    """Test that teachers cannot submit assignments"""
    teacher_id = setup_test_data["teacher_id"]
    class_id = setup_test_data["class_id"]
    
    # Teacher logs in and creates assignment
    teacher_login = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    teacher_token = teacher_login.json()["access_token"]
    
    assignment_data = {
        "class_id": class_id,
        "title": "Teacher Assignment",
        "type": "quiz",
        "questions": [
            {
                "type": "mcq",
                "prompt": "Test question?",
                "options": ["A", "B", "C", "D"],
                "answer_key": "A"
            }
        ]
    }
    
    create_response = client.post(
        "/api/assignments",
        json=assignment_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assignment_id = create_response.json()["id"]
    question_id = create_response.json()["questions"][0]["id"]
    
    # Teacher tries to submit assignment
    submission_data = {
        "answers": [
            {
                "question_id": question_id,
                "answer": "A"
            }
        ]
    }
    
    response = client.post(
        f"/api/assignments/{assignment_id}/submit",
        json=submission_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 403


def test_assignment_creation_validation(client: httpx.Client, setup_test_data):
    """Test assignment creation validation"""
    class_id = setup_test_data["class_id"]
    
    # Teacher logs in
    teacher_login = client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "password"
    })
    teacher_token = teacher_login.json()["access_token"]
    
    # Test missing required fields (missing title)
    invalid_assignment = {
        "class_id": class_id,
        "type": "quiz",
        "questions": []
        # Missing title field
    }
    
    response = client.post(
        "/api/assignments",
        json=invalid_assignment,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 422  # Validation error
    
    # Test missing type field
    invalid_assignment2 = {
        "class_id": class_id,
        "title": "Valid Title",
        "questions": []
        # Missing type field
    }
    
    response2 = client.post(
        "/api/assignments",
        json=invalid_assignment2,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response2.status_code == 422  # Validation error

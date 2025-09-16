"""
Test teacher override endpoints for responses and submissions
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.db.models import User, Class, Assignment, Question, Enrollment, Submission, Response
from sqlalchemy.orm import Session
import json
from datetime import datetime, timezone

client = TestClient(app)

def create_override_test_data(db: Session):
    """Create test data for teacher override testing"""
    
    # Create teacher user
    teacher = User(
        email="teacher@test.com",
        name="Test Teacher",
        role="teacher",
        hashed_password="$2b$12$test_hash"
    )
    db.add(teacher)
    db.flush()
    
    # Create student user
    student = User(
        email="student@test.com",
        name="Test Student",
        role="student",
        hashed_password="$2b$12$test_hash"
    )
    db.add(student)
    db.flush()
    
    # Create class
    test_class = Class(
        name="Test Biology Class",
        teacher_id=teacher.id,
        invite_code="TEST123"
    )
    db.add(test_class)
    db.flush()
    
    # Enroll student in class
    enrollment = Enrollment(
        class_id=test_class.id,
        student_id=student.id
    )
    db.add(enrollment)
    
    # Create assignment
    assignment = Assignment(
        class_id=test_class.id,
        title="Photosynthesis Quiz",
        type="quiz",
        rubric=json.dumps({
            "keywords": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen"]
        })
    )
    db.add(assignment)
    db.flush()
    
    # Create questions
    mcq_question = Question(
        assignment_id=assignment.id,
        type="mcq",
        prompt="What is the primary pigment in plants?",
        options=json.dumps(["Chlorophyll", "Carotene", "Xanthophyll", "Anthocyanin"]),
        answer_key="Chlorophyll",
        skill_tags=json.dumps(["chlorophyll", "plant_biology"])
    )
    db.add(mcq_question)
    db.flush()
    
    short_question = Question(
        assignment_id=assignment.id,
        type="short",
        prompt="Explain photosynthesis",
        answer_key="Plants use chlorophyll to capture light energy and convert carbon dioxide and water into glucose and oxygen through photosynthesis.",
        skill_tags=json.dumps(["photosynthesis", "chlorophyll"])
    )
    db.add(short_question)
    db.flush()
    
    # Create submission
    submission = Submission(
        assignment_id=assignment.id,
        student_id=student.id,
        submitted_at=datetime.now(timezone.utc),
        ai_score=0.6,  # Moderate AI score
        teacher_score=None
    )
    db.add(submission)
    db.flush()
    
    # Create responses
    mcq_response = Response(
        submission_id=submission.id,
        question_id=mcq_question.id,
        student_answer="Chlorophyll",
        ai_score=1.0,  # Correct MCQ
        teacher_score=None,
        ai_feedback="Correct answer"
    )
    db.add(mcq_response)
    db.flush()
    
    short_response = Response(
        submission_id=submission.id,
        question_id=short_question.id,
        student_answer="Plants use chlorophyll to make food from sunlight",
        ai_score=0.4,  # Low AI score
        teacher_score=None,
        ai_feedback="Answer is partially correct but missing key details about carbon dioxide and oxygen"
    )
    db.add(short_response)
    db.flush()
    
    db.commit()
    
    return {
        "teacher": teacher,
        "student": student,
        "class": test_class,
        "assignment": assignment,
        "submission": submission,
        "mcq_response": mcq_response,
        "short_response": short_response
    }


def test_override_response_score():
    """Test overriding a response score"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Override short response score
        override_data = {
            "teacher_score": 0.8,
            "teacher_feedback": "Student shows good understanding of the basic concept, but could improve on details."
        }
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "success" in data
        assert "message" in data
        assert "updated_item" in data
        
        assert data["success"] is True
        assert "successfully updated" in data["message"].lower()
        
        # Check updated response
        updated_response = data["updated_item"]
        assert updated_response["id"] == test_data["short_response"].id
        assert updated_response["teacher_score"] == 0.8
        assert updated_response["teacher_feedback"] == "Student shows good understanding of the basic concept, but could improve on details."
        assert updated_response["ai_score"] == 0.4  # AI score should remain unchanged
        assert updated_response["ai_feedback"] is not None  # AI feedback should remain
        
        # Verify in database
        db_response = db.query(Response).filter(Response.id == test_data["short_response"].id).first()
        assert db_response.teacher_score == 0.8
        assert db_response.teacher_feedback == "Student shows good understanding of the basic concept, but could improve on details."
        assert db_response.ai_score == 0.4  # AI score unchanged
        
    finally:
        db.close()


def test_override_response_without_feedback():
    """Test overriding a response score without feedback"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Override response score without feedback
        override_data = {
            "teacher_score": 0.9
        }
        
        response = client.post(
            f"/api/responses/{test_data['mcq_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # Check updated response
        updated_response = data["updated_item"]
        assert updated_response["teacher_score"] == 0.9
        assert updated_response["teacher_feedback"] is None  # No feedback provided
        
    finally:
        db.close()


def test_override_submission_score():
    """Test overriding a submission overall score"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Override submission score
        override_data = {
            "teacher_score": 0.85
        }
        
        response = client.post(
            f"/api/submissions/{test_data['submission'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "success" in data
        assert "message" in data
        assert "updated_item" in data
        
        assert data["success"] is True
        assert "successfully updated" in data["message"].lower()
        
        # Check updated submission
        updated_submission = data["updated_item"]
        assert updated_submission["id"] == test_data["submission"].id
        assert updated_submission["teacher_score"] == 0.85
        assert updated_submission["ai_score"] == 0.6  # AI score should remain unchanged
        
        # Verify in database
        db_submission = db.query(Submission).filter(Submission.id == test_data["submission"].id).first()
        assert db_submission.teacher_score == 0.85
        assert db_submission.ai_score == 0.6  # AI score unchanged
        
    finally:
        db.close()


def test_override_validation():
    """Test input validation for override endpoints"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Test invalid score range for response
        invalid_data = {
            "teacher_score": 1.5  # Invalid: > 1.0
        }
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=invalid_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test negative score
        invalid_data = {
            "teacher_score": -0.1  # Invalid: < 0
        }
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=invalid_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test missing score
        invalid_data = {}  # Missing required field
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=invalid_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test invalid submission score range
        invalid_data = {
            "teacher_score": 150  # Invalid: > 100
        }
        
        response = client.post(
            f"/api/submissions/{test_data['submission'].id}/override",
            json=invalid_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422  # Validation error
        
    finally:
        db.close()


def test_override_authorization():
    """Test authorization for override endpoints"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Test unauthorized access (no token)
        override_data = {"teacher_score": 0.8}
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data
        )
        assert response.status_code == 401
        
        response = client.post(
            f"/api/submissions/{test_data['submission'].id}/override",
            json=override_data
        )
        assert response.status_code == 401
        
        # Test student access (should be denied)
        student_login = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert student_login.status_code == 200
        student_token = student_login.json()["access_token"]
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403  # Forbidden for students
        
        response = client.post(
            f"/api/submissions/{test_data['submission'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403  # Forbidden for students
        
    finally:
        db.close()


def test_override_nonexistent_items():
    """Test override endpoints with non-existent items"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Test non-existent response
        override_data = {"teacher_score": 0.8}
        
        response = client.post(
            "/api/responses/99999/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 404
        
        # Test non-existent submission
        response = client.post(
            "/api/submissions/99999/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 404
        
    finally:
        db.close()


def test_override_wrong_teacher():
    """Test override endpoints with teacher who doesn't own the class"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Create another teacher
        other_teacher = User(
            email="other_teacher@test.com",
            name="Other Teacher",
            role="teacher",
            hashed_password="$2b$12$test_hash"
        )
        db.add(other_teacher)
        db.commit()
        
        # Login as other teacher
        login_response = client.post("/api/auth/login", json={
            "email": "other_teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        other_teacher_token = login_response.json()["access_token"]
        
        # Try to override (should be denied)
        override_data = {"teacher_score": 0.8}
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {other_teacher_token}"}
        )
        assert response.status_code == 403  # Forbidden - not the class owner
        
        response = client.post(
            f"/api/submissions/{test_data['submission'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {other_teacher_token}"}
        )
        assert response.status_code == 403  # Forbidden - not the class owner
        
    finally:
        db.close()


def test_override_multiple_times():
    """Test overriding the same item multiple times"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # First override
        override_data = {
            "teacher_score": 0.7,
            "teacher_feedback": "First override"
        }
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        
        # Second override
        override_data = {
            "teacher_score": 0.9,
            "teacher_feedback": "Second override - improved understanding"
        }
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        
        # Check final state
        updated_response = response.json()["updated_item"]
        assert updated_response["teacher_score"] == 0.9
        assert updated_response["teacher_feedback"] == "Second override - improved understanding"
        assert updated_response["ai_score"] == 0.4  # AI score should remain unchanged
        
        # Verify in database
        db_response = db.query(Response).filter(Response.id == test_data["short_response"].id).first()
        assert db_response.teacher_score == 0.9
        assert db_response.teacher_feedback == "Second override - improved understanding"
        assert db_response.ai_score == 0.4
        
    finally:
        db.close()


def test_override_edge_cases():
    """Test edge cases for override endpoints"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_override_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Test minimum score (0.0)
        override_data = {"teacher_score": 0.0}
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        assert response.json()["updated_item"]["teacher_score"] == 0.0
        
        # Test maximum score (1.0 for response, 100 for submission)
        override_data = {"teacher_score": 1.0}
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        assert response.json()["updated_item"]["teacher_score"] == 1.0
        
        # Test maximum submission score
        override_data = {"teacher_score": 100}
        
        response = client.post(
            f"/api/submissions/{test_data['submission'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        assert response.json()["updated_item"]["teacher_score"] == 100
        
        # Test very long feedback
        long_feedback = "This is a very long feedback message. " * 50  # Very long string
        override_data = {
            "teacher_score": 0.8,
            "teacher_feedback": long_feedback
        }
        
        response = client.post(
            f"/api/responses/{test_data['short_response'].id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 200
        assert response.json()["updated_item"]["teacher_feedback"] == long_feedback
        
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Test assignment submission with AI grading integration
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.db.models import User, Class, Assignment, Question, Enrollment
from sqlalchemy.orm import Session
import json

client = TestClient(app)

def create_test_data(db: Session):
    """Create test data for the assignment submission test"""
    
    # Create teacher user
    teacher = User(
        email="teacher@test.com",
        name="Test Teacher",
        role="teacher",
        hashed_password="$2b$12$test_hash"  # Mock hash
    )
    db.add(teacher)
    db.flush()
    
    # Create student user
    student = User(
        email="student@test.com",
        name="Test Student",
        role="student",
        hashed_password="$2b$12$test_hash"  # Mock hash
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
    
    # Create assignment with model answer and rubric
    assignment = Assignment(
        class_id=test_class.id,
        title="Photosynthesis Quiz",
        type="quiz",
        rubric=json.dumps({
            "keywords": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen", "photosynthesis"]
        }),
        due_at=None
    )
    db.add(assignment)
    db.flush()
    
    # Create MCQ question
    mcq_question = Question(
        assignment_id=assignment.id,
        type="mcq",
        prompt="What is the primary pigment responsible for capturing light energy in plants?",
        options=json.dumps([
            "Chlorophyll",
            "Carotene", 
            "Xanthophyll",
            "Anthocyanin"
        ]),
        answer_key="Chlorophyll",
        skill_tags=json.dumps(["chlorophyll", "photosynthesis", "plant_biology"])
    )
    db.add(mcq_question)
    db.flush()
    
    # Create short answer question with model answer
    short_question = Question(
        assignment_id=assignment.id,
        type="short",
        prompt="Explain the process of photosynthesis, including the key components and what is produced.",
        options=None,
        answer_key="Plants use chlorophyll to capture light energy from the sun and convert carbon dioxide and water into glucose and oxygen through photosynthesis. This process occurs in chloroplasts and requires sunlight as an energy source.",
        skill_tags=json.dumps(["chlorophyll", "sunlight", "carbon_dioxide", "oxygen", "photosynthesis", "plant_biology"])
    )
    db.add(short_question)
    db.flush()
    
    db.commit()
    
    return {
        "teacher": teacher,
        "student": student,
        "class": test_class,
        "assignment": assignment,
        "mcq_question": mcq_question,
        "short_question": short_question
    }


def test_submit_assignment_with_ai_grading():
    """Test submitting an assignment with AI grading for short answers"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_test_data(db)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        student_token = login_response.json()["access_token"]
        
        # Submit assignment with both MCQ and short answer
        submission_data = {
            "answers": [
                {
                    "question_id": test_data["mcq_question"].id,
                    "answer": "Chlorophyll"  # Correct MCQ answer
                },
                {
                    "question_id": test_data["short_question"].id,
                    "answer": "Plants use chlorophyll to capture sunlight and convert carbon dioxide and water into glucose and oxygen through photosynthesis. This happens in chloroplasts and needs light energy."  # Good short answer
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check submission structure
        assert "id" in data
        assert "assignment_id" in data
        assert "student_id" in data
        assert "submitted_at" in data
        assert "ai_score" in data
        assert "teacher_score" in data
        assert "breakdown" in data
        
        # Check AI score is calculated (should be average of MCQ 1.0 and short answer ~0.8+)
        assert data["ai_score"] is not None
        assert 0.8 <= data["ai_score"] <= 1.0
        
        # Check breakdown structure
        breakdown = data["breakdown"]
        assert len(breakdown) == 2  # Two questions
        
        # Find MCQ and short answer responses
        mcq_response = next(r for r in breakdown if r["type"] == "mcq")
        short_response = next(r for r in breakdown if r["type"] == "short")
        
        # Check MCQ response
        assert mcq_response["question_id"] == test_data["mcq_question"].id
        assert mcq_response["type"] == "mcq"
        assert mcq_response["score"] == 1.0  # Correct answer
        assert mcq_response["is_mcq_correct"] is True
        
        # Check short answer response
        assert short_response["question_id"] == test_data["short_question"].id
        assert short_response["type"] == "short"
        assert short_response["score"] is not None
        assert 0.7 <= short_response["score"] <= 1.0  # Good answer should score high
        assert "ai_feedback" in short_response
        assert short_response["ai_feedback"] is not None
        assert len(short_response["ai_feedback"]) > 10
        assert "matched_keywords" in short_response
        assert isinstance(short_response["matched_keywords"], list)
        assert len(short_response["matched_keywords"]) >= 4  # Should match most keywords
        
    finally:
        db.close()


def test_submit_assignment_weak_short_answer():
    """Test submitting an assignment with a weak short answer"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_test_data(db)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        student_token = login_response.json()["access_token"]
        
        # Submit assignment with weak short answer
        submission_data = {
            "answers": [
                {
                    "question_id": test_data["mcq_question"].id,
                    "answer": "Chlorophyll"  # Correct MCQ answer
                },
                {
                    "question_id": test_data["short_question"].id,
                    "answer": "Plants make food using light."  # Weak short answer
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check AI score is lower due to weak short answer
        assert data["ai_score"] is not None
        assert 0.3 <= data["ai_score"] <= 0.7  # Lower score due to weak short answer
        
        # Check breakdown
        breakdown = data["breakdown"]
        short_response = next(r for r in breakdown if r["type"] == "short")
        
        # Check short answer response has lower score
        assert short_response["score"] is not None
        assert short_response["score"] < 0.7  # Below threshold
        assert "ai_feedback" in short_response
        assert "matched_keywords" in short_response
        assert len(short_response["matched_keywords"]) < 3  # Fewer keywords matched
        
    finally:
        db.close()


def test_submit_assignment_incorrect_mcq():
    """Test submitting an assignment with incorrect MCQ answer"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_test_data(db)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        student_token = login_response.json()["access_token"]
        
        # Submit assignment with incorrect MCQ
        submission_data = {
            "answers": [
                {
                    "question_id": test_data["mcq_question"].id,
                    "answer": "Carotene"  # Incorrect MCQ answer
                },
                {
                    "question_id": test_data["short_question"].id,
                    "answer": "Plants use chlorophyll to capture sunlight and convert carbon dioxide and water into glucose and oxygen through photosynthesis."
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check AI score is lower due to incorrect MCQ
        assert data["ai_score"] is not None
        assert 0.4 <= data["ai_score"] <= 0.9  # Lower due to incorrect MCQ
        
        # Check breakdown
        breakdown = data["breakdown"]
        mcq_response = next(r for r in breakdown if r["type"] == "mcq")
        
        # Check MCQ response is marked incorrect
        assert mcq_response["score"] == 0.0
        assert mcq_response["is_mcq_correct"] is False
        
    finally:
        db.close()


def test_submit_assignment_missing_model_answer():
    """Test submitting to assignment with missing model answer"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_test_data(db)
        
        # Update short question to have no model answer
        test_data["short_question"].answer_key = None
        db.commit()
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        student_token = login_response.json()["access_token"]
        
        # Submit assignment
        submission_data = {
            "answers": [
                {
                    "question_id": test_data["mcq_question"].id,
                    "answer": "Chlorophyll"
                },
                {
                    "question_id": test_data["short_question"].id,
                    "answer": "Plants use chlorophyll for photosynthesis."
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check breakdown
        breakdown = data["breakdown"]
        short_response = next(r for r in breakdown if r["type"] == "short")
        
        # Check short answer response has null score due to missing model answer
        assert short_response["score"] is None
        assert short_response["ai_feedback"] == "Model/rubric missing"
        assert short_response["matched_keywords"] == []
        
        # AI score should only consider MCQ (1.0)
        assert data["ai_score"] == 1.0
        
    finally:
        db.close()


def test_submit_assignment_validation():
    """Test input validation for assignment submission"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_test_data(db)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        student_token = login_response.json()["access_token"]
        
        # Test missing answers
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json={"answers": []},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 400
        
        # Test invalid question ID
        submission_data = {
            "answers": [
                {
                    "question_id": 99999,  # Non-existent question
                    "answer": "Test answer"
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 400
        
        # Test missing authorization
        response = client.post(
            f"/api/assignments/{test_data['assignment'].id}/submit",
            json=submission_data
        )
        assert response.status_code == 401
        
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

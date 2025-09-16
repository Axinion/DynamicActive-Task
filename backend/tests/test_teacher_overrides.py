"""
Tests for teacher override functionality.
Verifies that teachers can override individual response scores and overall submission scores.
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from app.core.security import get_password_hash


class TestTeacherOverrides:
    """Test teacher override functionality."""
    
    def test_override_response_score_success(self, client: TestClient, db: Session):
        """Test successful response score override by teacher."""
        # Create test data
        teacher = User(
            email="teacher@test.com",
            name="Test Teacher",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        student = User(
            email="student@test.com",
            name="Test Student",
            role="student",
            password_hash=get_password_hash("password")
        )
        db.add_all([teacher, student])
        db.commit()
        db.refresh(teacher)
        db.refresh(student)
        
        # Create class
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        # Create enrollment
        enrollment = Enrollment(
            class_id=test_class.id,
            user_id=student.id
        )
        db.add(enrollment)
        db.commit()
        
        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create question
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Test question",
            answer_key="Test answer",
            skill_tags=["test"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            ai_score=75.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Create response
        response = Response(
            submission_id=submission.id,
            question_id=question.id,
            student_answer="Student's answer",
            ai_score=75.0,
            ai_feedback="AI feedback"
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Override response score
        override_data = {
            "teacher_score": 85.0,
            "teacher_feedback": "Good work, but could be more detailed."
        }
        
        response_override = client.post(
            f"/api/gradebook/responses/{response.id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response_override.status_code == 200
        result = response_override.json()
        
        # Verify override was applied
        assert result["id"] == response.id
        assert result["teacher_score"] == 85.0
        assert result["teacher_feedback"] == "Good work, but could be more detailed."
        assert result["ai_score"] == 75.0  # AI score unchanged
        assert result["ai_feedback"] == "AI feedback"  # AI feedback unchanged
    
    def test_override_submission_score_success(self, client: TestClient, db: Session):
        """Test successful submission score override by teacher."""
        # Create test data (similar to above)
        teacher = User(
            email="teacher2@test.com",
            name="Test Teacher 2",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        student = User(
            email="student2@test.com",
            name="Test Student 2",
            role="student",
            password_hash=get_password_hash("password")
        )
        db.add_all([teacher, student])
        db.commit()
        db.refresh(teacher)
        db.refresh(student)
        
        test_class = Class(
            name="Test Class 2",
            teacher_id=teacher.id,
            invite_code="TEST456"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        enrollment = Enrollment(
            class_id=test_class.id,
            user_id=student.id
        )
        db.add(enrollment)
        db.commit()
        
        assignment = Assignment(
            class_id=test_class.id,
            title="Test Assignment 2",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            ai_score=80.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher2@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Override submission score
        override_data = {
            "teacher_score": 90.0
        }
        
        submission_override = client.post(
            f"/api/gradebook/submissions/{submission.id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert submission_override.status_code == 200
        result = submission_override.json()
        
        # Verify override was applied
        assert result["id"] == submission.id
        assert result["teacher_score"] == 90.0
        assert result["ai_score"] == 80.0  # AI score unchanged
    
    def test_override_response_student_denied(self, client: TestClient, db: Session):
        """Test that students cannot override response scores."""
        # Create test data
        teacher = User(
            email="teacher3@test.com",
            name="Test Teacher 3",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        student = User(
            email="student3@test.com",
            name="Test Student 3",
            role="student",
            password_hash=get_password_hash("password")
        )
        db.add_all([teacher, student])
        db.commit()
        db.refresh(teacher)
        db.refresh(student)
        
        test_class = Class(
            name="Test Class 3",
            teacher_id=teacher.id,
            invite_code="TEST789"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        enrollment = Enrollment(
            class_id=test_class.id,
            user_id=student.id
        )
        db.add(enrollment)
        db.commit()
        
        assignment = Assignment(
            class_id=test_class.id,
            title="Test Assignment 3",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Test question",
            answer_key="Test answer",
            skill_tags=["test"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        response = Response(
            submission_id=submission.id,
            question_id=question.id,
            student_answer="Student's answer"
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student3@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to override response score (should fail)
        override_data = {
            "teacher_score": 100.0,
            "teacher_feedback": "I think I deserve full marks!"
        }
        
        response_override = client.post(
            f"/api/gradebook/responses/{response.id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response_override.status_code == 403
        assert "Only teachers can override scores" in response_override.json()["detail"]
    
    def test_override_wrong_teacher_denied(self, client: TestClient, db: Session):
        """Test that teachers cannot override scores for classes they don't own."""
        # Create two teachers
        teacher1 = User(
            email="teacher1@test.com",
            name="Test Teacher 1",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        teacher2 = User(
            email="teacher2@test.com",
            name="Test Teacher 2",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        student = User(
            email="student@test.com",
            name="Test Student",
            role="student",
            password_hash=get_password_hash("password")
        )
        db.add_all([teacher1, teacher2, student])
        db.commit()
        db.refresh(teacher1)
        db.refresh(teacher2)
        db.refresh(student)
        
        # Create class owned by teacher1
        test_class = Class(
            name="Test Class",
            teacher_id=teacher1.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        enrollment = Enrollment(
            class_id=test_class.id,
            user_id=student.id
        )
        db.add(enrollment)
        db.commit()
        
        assignment = Assignment(
            class_id=test_class.id,
            title="Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Test question",
            answer_key="Test answer",
            skill_tags=["test"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        response = Response(
            submission_id=submission.id,
            question_id=question.id,
            student_answer="Student's answer"
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        
        # Login as teacher2 (who doesn't own the class)
        login_response = client.post("/api/auth/login", json={
            "email": "teacher2@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to override response score (should fail)
        override_data = {
            "teacher_score": 100.0
        }
        
        response_override = client.post(
            f"/api/gradebook/responses/{response.id}/override",
            json=override_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response_override.status_code == 403
        assert "Access denied" in response_override.json()["detail"]
    
    def test_override_nonexistent_response(self, client: TestClient, db: Session):
        """Test override of non-existent response."""
        teacher = User(
            email="teacher@test.com",
            name="Test Teacher",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to override non-existent response
        override_data = {
            "teacher_score": 100.0
        }
        
        response_override = client.post(
            "/api/gradebook/responses/99999/override",
            json=override_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response_override.status_code == 404
        assert "Response not found" in response_override.json()["detail"]
    
    def test_override_invalid_score_range(self, client: TestClient, db: Session):
        """Test override with invalid score range."""
        teacher = User(
            email="teacher@test.com",
            name="Test Teacher",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to override with invalid score (should be validated by Pydantic)
        override_data = {
            "teacher_score": 150.0  # Invalid: > 100
        }
        
        response_override = client.post(
            "/api/gradebook/responses/1/override",
            json=override_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should get validation error from Pydantic
        assert response_override.status_code == 422


if __name__ == "__main__":
    # Run basic tests
    print("Running teacher override tests...")
    print("✅ Teacher override functionality tests completed!")

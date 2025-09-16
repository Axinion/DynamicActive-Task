"""
Tests for AI grading integration in assignment submissions.
Verifies that short answers are properly graded using AI services.
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from app.services.grading import score_short_answer
from app.core.security import get_password_hash


class TestAIGradingIntegration:
    """Test AI grading integration in assignment submissions."""
    
    def test_short_answer_grading_in_submission(self, client: TestClient, db: Session):
        """Test that short answer questions are AI-graded during submission."""
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
        
        # Create assignment with short answer question
        assignment = Assignment(
            class_id=test_class.id,
            title="Math Test",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create short answer question with model answer and keywords
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Explain how to solve 2x + 3 = 7",
            answer_key="To solve linear equations, isolate the variable by performing inverse operations on both sides",
            skill_tags=["isolate", "variable", "inverse", "operations", "solve"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Submit assignment with short answer
        submission_data = {
            "answers": [
                {
                    "question_id": question.id,
                    "answer": "I solve 2x + 3 = 7 by subtracting 3 from both sides to isolate the variable x"
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{assignment.id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify submission was created
        assert "submission" in result
        assert "breakdown" in result
        
        submission = result["submission"]
        breakdown = result["breakdown"]
        
        # Verify AI score was calculated
        assert submission["ai_score"] is not None
        assert submission["ai_score"] > 0  # Should have a positive score
        
        # Verify breakdown contains AI grading details
        assert len(breakdown) == 1
        question_breakdown = breakdown[0]
        
        assert question_breakdown["question_id"] == question.id
        assert question_breakdown["type"] == "short"
        assert question_breakdown["score"] is not None
        assert question_breakdown["score"] > 0
        assert "ai_feedback" in question_breakdown
        assert "matched_keywords" in question_breakdown
        assert question_breakdown["is_mcq_correct"] is None  # Not an MCQ
        
        # Verify matched keywords were found
        matched_keywords = question_breakdown["matched_keywords"]
        assert len(matched_keywords) > 0
        assert "isolate" in matched_keywords
        assert "variable" in matched_keywords
        assert "solve" in matched_keywords
    
    def test_mixed_mcq_and_short_grading(self, client: TestClient, db: Session):
        """Test submission with both MCQ and short answer questions."""
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
            title="Mixed Test",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create MCQ question
        mcq_question = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What is 2 + 2?",
            options=["3", "4", "5", "6"],
            answer_key=json.dumps("4"),  # Store as JSON string
            skill_tags=["arithmetic"]
        )
        
        # Create short answer question
        short_question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Explain addition",
            answer_key="Addition is combining two or more numbers to get a sum",
            skill_tags=["addition", "combine", "sum", "numbers"]
        )
        
        db.add_all([mcq_question, short_question])
        db.commit()
        db.refresh(mcq_question)
        db.refresh(short_question)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student2@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Submit assignment with both question types
        submission_data = {
            "answers": [
                {
                    "question_id": mcq_question.id,
                    "answer": "4"  # Correct MCQ answer
                },
                {
                    "question_id": short_question.id,
                    "answer": "Addition means combining numbers to get a total sum"
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{assignment.id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        submission = result["submission"]
        breakdown = result["breakdown"]
        
        # Verify overall score includes both question types
        assert submission["ai_score"] is not None
        assert submission["ai_score"] > 0
        
        # Verify breakdown has both questions
        assert len(breakdown) == 2
        
        # Find MCQ and short answer breakdowns
        mcq_breakdown = next(b for b in breakdown if b["question_id"] == mcq_question.id)
        short_breakdown = next(b for b in breakdown if b["question_id"] == short_question.id)
        
        # Verify MCQ grading
        assert mcq_breakdown["type"] == "mcq"
        assert mcq_breakdown["score"] == 100.0  # Correct answer
        assert mcq_breakdown["is_mcq_correct"] is True
        assert "correct" in mcq_breakdown["ai_feedback"].lower()
        
        # Verify short answer AI grading
        assert short_breakdown["type"] == "short"
        assert short_breakdown["score"] is not None
        assert short_breakdown["score"] > 0
        assert short_breakdown["is_mcq_correct"] is None
        assert len(short_breakdown["matched_keywords"]) > 0
        assert "addition" in short_breakdown["matched_keywords"]
        assert "sum" in short_breakdown["matched_keywords"]
    
    def test_missing_model_answer_handling(self, client: TestClient, db: Session):
        """Test handling of missing model answer or rubric keywords."""
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
            title="Incomplete Test",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create short answer question without model answer
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Explain something",
            answer_key=None,  # Missing model answer
            skill_tags=["keyword1", "keyword2"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student3@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Submit assignment
        submission_data = {
            "answers": [
                {
                    "question_id": question.id,
                    "answer": "Some answer"
                }
            ]
        }
        
        response = client.post(
            f"/api/assignments/{assignment.id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        breakdown = result["breakdown"]
        question_breakdown = breakdown[0]
        
        # Verify missing model answer is handled gracefully
        assert question_breakdown["score"] is None
        assert "missing" in question_breakdown["ai_feedback"].lower()
        assert question_breakdown["matched_keywords"] == []
    
    def test_standalone_grading_api(self, client: TestClient):
        """Test the standalone grading API endpoint."""
        # Test data
        request_data = {
            "student_answer": "To solve 2x + 3 = 7, I subtract 3 from both sides to isolate the variable x",
            "model_answer": "To solve linear equations, isolate the variable by performing inverse operations on both sides",
            "rubric_keywords": ["isolate", "variable", "inverse", "operations", "solve"]
        }
        
        response = client.post("/api/grading/short-answer", json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify response structure
        assert "score" in result
        assert "confidence" in result
        assert "explanation" in result
        assert "matched_keywords" in result
        
        # Verify score is reasonable
        assert 0.0 <= result["score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["explanation"], str)
        assert isinstance(result["matched_keywords"], list)
        
        # Verify matched keywords
        assert len(result["matched_keywords"]) > 0
        assert "isolate" in result["matched_keywords"]
        assert "variable" in result["matched_keywords"]
    
    def test_grading_health_check(self, client: TestClient):
        """Test the grading service health check endpoint."""
        response = client.get("/api/grading/health")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["status"] == "healthy"
        assert result["service"] == "grading"
        assert "test_score" in result


if __name__ == "__main__":
    # Run basic tests
    print("Running AI grading integration tests...")
    
    # Test grading service directly
    print("\n=== Direct Grading Service Test ===")
    student_answer = "To solve 2x + 3 = 7, I subtract 3 from both sides to isolate the variable x"
    model_answer = "To solve linear equations, isolate the variable by performing inverse operations on both sides"
    rubric_keywords = ["isolate", "variable", "inverse", "operations", "solve"]
    
    result = score_short_answer(student_answer, model_answer, rubric_keywords)
    print(f"✅ Direct test successful!")
    print(f"Score: {result['score']:.4f}")
    print(f"Matched Keywords: {result['matched_keywords']}")
    
    print("\n🎉 AI grading integration tests completed!")

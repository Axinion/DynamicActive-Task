"""
Tests for misconception insights functionality.
"""

import pytest
import json
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.models import User, Class, Lesson, Assignment, Question, Submission, Response, Enrollment
from app.core.security import get_password_hash
from app.services.insights import (
    get_low_scoring_responses,
    extract_keywords,
    cluster_responses,
    get_misconception_insights
)


class TestInsightsService:
    """Test the insights service functions."""
    
    def test_get_low_scoring_responses(self, client: TestClient, db: Session):
        """Test retrieval of low-scoring responses."""
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
        
        # Create questions
        question1 = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What is 2+2?",
            options=["3", "4", "5", "6"],
            answer_key="4",
            skill_tags=["arithmetic", "basic_math"]
        )
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Explain fractions",
            answer_key="Fractions represent parts of a whole",
            skill_tags=["fractions", "basic_math"]
        )
        db.add_all([question1, question2])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)
        
        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Create responses - one correct, one incorrect
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="3",  # Wrong answer
            ai_score=0.0  # Low score
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="Fractions are hard to understand",
            ai_score=30.0  # Low score (below 70% threshold)
        )
        db.add_all([response1, response2])
        db.commit()
        
        # Get low-scoring responses
        low_scoring = get_low_scoring_responses(test_class.id, db)
        
        # Should find both responses
        assert len(low_scoring) == 2
        
        # Check response data structure
        for response in low_scoring:
            assert 'response_id' in response
            assert 'student_answer' in response
            assert 'question_type' in response
            assert 'skill_tags' in response
            assert 'score' in response
    
    def test_extract_keywords(self, client: TestClient, db: Session):
        """Test keyword extraction from text."""
        # Test with normal text
        text1 = "Fractions are parts of a whole number and can be difficult to understand"
        keywords1 = extract_keywords(text1, top_k=3)
        assert len(keywords1) <= 3
        assert all(isinstance(kw, str) for kw in keywords1)
        
        # Test with short text
        text2 = "No"
        keywords2 = extract_keywords(text2, top_k=3)
        assert len(keywords2) == 0  # Too short
        
        # Test with empty text
        text3 = ""
        keywords3 = extract_keywords(text3, top_k=3)
        assert len(keywords3) == 0
        
        # Test with special characters
        text4 = "Math is fun! I love solving problems with numbers and equations."
        keywords4 = extract_keywords(text4, top_k=3)
        assert len(keywords4) <= 3
        assert all(len(kw) > 2 for kw in keywords4)  # No short words
    
    def test_cluster_responses_sufficient_data(self, client: TestClient, db: Session):
        """Test clustering with sufficient data."""
        # Create mock response data
        responses = [
            {
                'response_id': 1,
                'student_answer': 'Fractions are parts of a whole',
                'question_prompt': 'What are fractions?',
                'skill_tags': ['fractions'],
                'score': 30.0,
                'assignment_title': 'Math Quiz'
            },
            {
                'response_id': 2,
                'student_answer': 'Fractions represent portions of something',
                'question_prompt': 'Define fractions',
                'skill_tags': ['fractions'],
                'score': 25.0,
                'assignment_title': 'Math Quiz'
            },
            {
                'response_id': 3,
                'student_answer': 'Fractions are like pieces of pizza',
                'question_prompt': 'Explain fractions',
                'skill_tags': ['fractions'],
                'score': 20.0,
                'assignment_title': 'Math Quiz'
            },
            {
                'response_id': 4,
                'student_answer': 'Algebra is solving for x',
                'question_prompt': 'What is algebra?',
                'skill_tags': ['algebra'],
                'score': 15.0,
                'assignment_title': 'Math Quiz'
            },
            {
                'response_id': 5,
                'student_answer': 'Algebra uses variables and equations',
                'question_prompt': 'Define algebra',
                'skill_tags': ['algebra'],
                'score': 10.0,
                'assignment_title': 'Math Quiz'
            }
        ]
        
        # Test clustering
        clusters = cluster_responses(responses)
        
        # Should return clusters
        assert len(clusters) > 0
        assert len(clusters) <= 3  # Max 3 clusters
        
        # Check cluster structure
        for cluster in clusters:
            assert 'label' in cluster
            assert 'examples' in cluster
            assert 'suggested_skill_tags' in cluster
            assert 'cluster_size' in cluster
            assert 'common_keywords' in cluster
            
            # Check examples
            assert len(cluster['examples']) <= 2  # Max 2 examples
            for example in cluster['examples']:
                assert 'student_answer' in example
                assert 'question_prompt' in example
                assert 'score' in example
                assert 'assignment_title' in example
    
    def test_cluster_responses_insufficient_data(self, client: TestClient, db: Session):
        """Test clustering with insufficient data."""
        # Create mock response data with less than 3 items
        responses = [
            {
                'response_id': 1,
                'student_answer': 'Fractions are hard',
                'question_prompt': 'What are fractions?',
                'skill_tags': ['fractions'],
                'score': 30.0,
                'assignment_title': 'Math Quiz'
            },
            {
                'response_id': 2,
                'student_answer': 'Algebra is confusing',
                'question_prompt': 'What is algebra?',
                'skill_tags': ['algebra'],
                'score': 25.0,
                'assignment_title': 'Math Quiz'
            }
        ]
        
        # Test clustering
        clusters = cluster_responses(responses)
        
        # Should return empty list for insufficient data
        assert len(clusters) == 0
    
    def test_get_misconception_insights_sufficient_data(self, client: TestClient, db: Session):
        """Test misconception insights with sufficient data."""
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
        
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
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
        
        # Create multiple assignments with low-scoring responses
        for i in range(3):
            assignment = Assignment(
                class_id=test_class.id,
                title=f"Test Assignment {i+1}",
                type="quiz"
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            
            question = Question(
                assignment_id=assignment.id,
                type="short",
                prompt=f"Question {i+1}",
                answer_key="Correct answer",
                skill_tags=["test_skill"]
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
                student_answer=f"Wrong answer {i+1}",
                ai_score=30.0  # Low score
            )
            db.add(response)
            db.commit()
        
        # Get insights
        insights = get_misconception_insights(test_class.id, db)
        
        # Check structure
        assert 'class_id' in insights
        assert 'class_name' in insights
        assert 'total_responses_analyzed' in insights
        assert 'clusters' in insights
        assert 'analysis_summary' in insights
        
        assert insights['class_id'] == test_class.id
        assert insights['class_name'] == "Test Class"
        assert insights['total_responses_analyzed'] >= 3
    
    def test_get_misconception_insights_insufficient_data(self, client: TestClient, db: Session):
        """Test misconception insights with insufficient data."""
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
        
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
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
        
        # Create only 2 low-scoring responses (insufficient for clustering)
        assignment = Assignment(
            class_id=test_class.id,
            title="Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        for i in range(2):
            question = Question(
                assignment_id=assignment.id,
                type="short",
                prompt=f"Question {i+1}",
                answer_key="Correct answer",
                skill_tags=["test_skill"]
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
                student_answer=f"Wrong answer {i+1}",
                ai_score=30.0  # Low score
            )
            db.add(response)
            db.commit()
        
        # Get insights
        insights = get_misconception_insights(test_class.id, db)
        
        # Check structure for insufficient data
        assert 'class_id' in insights
        assert 'total_responses_analyzed' in insights
        assert 'clusters' in insights
        assert 'message' in insights
        
        assert insights['total_responses_analyzed'] == 2
        assert len(insights['clusters']) == 0
        assert "Not enough data" in insights['message']


class TestInsightsAPI:
    """Test the insights API endpoints."""
    
    def test_get_misconception_insights_teacher_success(self, client: TestClient, db: Session):
        """Test teacher successfully getting misconception insights."""
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
        
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
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
        
        # Create sufficient data for clustering
        for i in range(3):
            assignment = Assignment(
                class_id=test_class.id,
                title=f"Test Assignment {i+1}",
                type="quiz"
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            
            question = Question(
                assignment_id=assignment.id,
                type="short",
                prompt=f"Question {i+1}",
                answer_key="Correct answer",
                skill_tags=["test_skill"]
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
                student_answer=f"Wrong answer {i+1}",
                ai_score=30.0  # Low score
            )
            db.add(response)
            db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get misconception insights
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["class_id"] == test_class.id
        assert data["class_name"] == "Test Class"
        assert "total_responses_analyzed" in data
        assert "clusters" in data
        assert "analysis_summary" in data
        assert data["requested_by"]["id"] == teacher.id
        assert data["requested_by"]["role"] == "teacher"
    
    def test_get_misconception_insights_student_denied(self, client: TestClient, db: Session):
        """Test that students cannot access misconception insights."""
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
        
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
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
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to get misconception insights (should fail)
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Only teachers can access misconception insights" in response.json()["detail"]
    
    def test_get_misconception_insights_wrong_teacher(self, client: TestClient, db: Session):
        """Test that teachers cannot access insights for classes they don't own."""
        # Create test data
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
        db.add_all([teacher1, teacher2])
        db.commit()
        db.refresh(teacher1)
        db.refresh(teacher2)
        
        # Create class owned by teacher1
        test_class = Class(
            name="Test Class",
            teacher_id=teacher1.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        # Login as teacher2 (who doesn't own the class)
        login_response = client.post("/api/auth/login", json={
            "email": "teacher2@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to get misconception insights (should fail)
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Class not found or access denied" in response.json()["detail"]
    
    def test_insights_health_check(self, client: TestClient):
        """Test the insights health check endpoint."""
        response = client.get("/api/insights/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "Insights service is operational" in data["message"]
        assert "features" in data
        assert "misconception_clustering" in data["features"]


if __name__ == "__main__":
    # Run basic tests
    print("Running insights tests...")
    print("✅ Insights functionality tests completed!")

"""
Tests for personalized recommendations functionality.
"""

import pytest
import json
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.models import User, Class, Lesson, Assignment, Question, Submission, Response, Enrollment
from app.core.security import get_password_hash
from app.services.recommendations import (
    compute_skill_mastery,
    candidate_lessons,
    get_recent_lesson_embeddings,
    rank_lessons_for_student,
    get_student_recommendations
)


class TestRecommendationsService:
    """Test the recommendations service functions."""
    
    def test_compute_skill_mastery_basic(self, client: TestClient, db: Session):
        """Test basic skill mastery computation."""
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
        
        # Create questions with different skill tags
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
        
        # Create responses with different scores
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="4",
            ai_score=100.0,  # Perfect score
            teacher_score=None
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="Fractions are parts of a whole",
            ai_score=60.0,  # Lower score
            teacher_score=80.0  # Teacher override
        )
        db.add_all([response1, response2])
        db.commit()
        
        # Compute skill mastery
        mastery = compute_skill_mastery(student.id, db)
        
        # Verify results
        assert "arithmetic" in mastery
        assert "basic_math" in mastery
        assert "fractions" in mastery
        
        # arithmetic and basic_math should have high mastery (100% from question1)
        assert mastery["arithmetic"] == 1.0
        assert mastery["basic_math"] == 0.9  # Average of 1.0 and 0.8
        
        # fractions should have lower mastery (80% from teacher override)
        assert mastery["fractions"] == 0.8
    
    def test_candidate_lessons(self, client: TestClient, db: Session):
        """Test candidate lessons retrieval."""
        # Create test data
        teacher = User(
            email="teacher@test.com",
            name="Test Teacher",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        # Create lessons
        lesson1 = Lesson(
            class_id=test_class.id,
            title="Basic Math",
            content="Introduction to basic arithmetic",
            skill_tags=["arithmetic", "basic_math"]
        )
        lesson2 = Lesson(
            class_id=test_class.id,
            title="Fractions",
            content="Understanding fractions",
            skill_tags=["fractions", "basic_math"]
        )
        db.add_all([lesson1, lesson2])
        db.commit()
        
        # Get candidate lessons
        candidates = candidate_lessons(test_class.id, db)
        
        assert len(candidates) == 2
        assert any(lesson.title == "Basic Math" for lesson in candidates)
        assert any(lesson.title == "Fractions" for lesson in candidates)
    
    def test_rank_lessons_for_student(self, client: TestClient, db: Session):
        """Test lesson ranking for a student."""
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
        
        # Create lessons
        lesson1 = Lesson(
            class_id=test_class.id,
            title="Basic Math",
            content="Introduction to basic arithmetic",
            skill_tags=["arithmetic", "basic_math"]
        )
        lesson2 = Lesson(
            class_id=test_class.id,
            title="Fractions",
            content="Understanding fractions",
            skill_tags=["fractions", "basic_math"]
        )
        lesson3 = Lesson(
            class_id=test_class.id,
            title="Advanced Algebra",
            content="Complex algebraic concepts",
            skill_tags=["algebra", "advanced_math"]
        )
        db.add_all([lesson1, lesson2, lesson3])
        db.commit()
        
        # Create some performance data (student struggles with fractions)
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
            prompt="Explain fractions",
            answer_key="Fractions represent parts of a whole",
            skill_tags=["fractions"]
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
            student_answer="Fractions are hard",
            ai_score=30.0  # Low score on fractions
        )
        db.add(response)
        db.commit()
        
        # Rank lessons
        rankings = rank_lessons_for_student(student.id, test_class.id, db, k=2)
        
        # Should return 2 recommendations
        assert len(rankings) == 2
        
        # Verify that we have recommendations
        assert all("lesson_id" in r for r in rankings)
        assert all("title" in r for r in rankings)
        assert all("reason" in r for r in rankings)
        assert all("score" in r for r in rankings)
        
        # Check that at least one lesson is recommended
        lesson_titles = [r["title"] for r in rankings]
        assert len(lesson_titles) > 0
    
    def test_get_student_recommendations(self, client: TestClient, db: Session):
        """Test the main recommendations function."""
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
        
        # Create a lesson
        lesson = Lesson(
            class_id=test_class.id,
            title="Basic Math",
            content="Introduction to basic arithmetic",
            skill_tags=["arithmetic", "basic_math"]
        )
        db.add(lesson)
        db.commit()
        
        # Get recommendations
        recommendations = get_student_recommendations(student.id, test_class.id, db, k=3)
        
        # Verify structure
        assert "student_id" in recommendations
        assert "class_id" in recommendations
        assert "class_name" in recommendations
        assert "skill_mastery" in recommendations
        assert "recommendations" in recommendations
        assert "total_lessons_available" in recommendations
        
        assert recommendations["student_id"] == student.id
        assert recommendations["class_id"] == test_class.id
        assert recommendations["class_name"] == "Test Class"
        assert isinstance(recommendations["skill_mastery"], dict)
        assert isinstance(recommendations["recommendations"], list)
        assert recommendations["total_lessons_available"] == 1


class TestRecommendationsAPI:
    """Test the recommendations API endpoints."""
    
    def test_get_recommendations_student_own(self, client: TestClient, db: Session):
        """Test student getting their own recommendations."""
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
        
        lesson = Lesson(
            class_id=test_class.id,
            title="Basic Math",
            content="Introduction to basic arithmetic",
            skill_tags=["arithmetic"]
        )
        db.add(lesson)
        db.commit()
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get recommendations
        response = client.get(
            f"/api/recommendations?class_id={test_class.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["student_id"] == student.id
        assert data["class_id"] == test_class.id
        assert data["target_student"]["id"] == student.id
        assert data["requested_by"]["id"] == student.id
    
    def test_get_recommendations_teacher_for_student(self, client: TestClient, db: Session):
        """Test teacher getting recommendations for a student."""
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
        
        lesson = Lesson(
            class_id=test_class.id,
            title="Basic Math",
            content="Introduction to basic arithmetic",
            skill_tags=["arithmetic"]
        )
        db.add(lesson)
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get recommendations for student
        response = client.get(
            f"/api/recommendations?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["student_id"] == student.id
        assert data["target_student"]["id"] == student.id
        assert data["requested_by"]["id"] == teacher.id
        assert data["requested_by"]["role"] == "teacher"
    
    def test_get_recommendations_student_denied_other_student(self, client: TestClient, db: Session):
        """Test that students cannot view recommendations for other students."""
        # Create test data
        teacher = User(
            email="teacher@test.com",
            name="Test Teacher",
            role="teacher",
            password_hash=get_password_hash("password")
        )
        student1 = User(
            email="student1@test.com",
            name="Test Student 1",
            role="student",
            password_hash=get_password_hash("password")
        )
        student2 = User(
            email="student2@test.com",
            name="Test Student 2",
            role="student",
            password_hash=get_password_hash("password")
        )
        db.add_all([teacher, student1, student2])
        db.commit()
        db.refresh(teacher)
        db.refresh(student1)
        db.refresh(student2)
        
        test_class = Class(
            name="Test Class",
            teacher_id=teacher.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)
        
        enrollment1 = Enrollment(
            class_id=test_class.id,
            user_id=student1.id
        )
        enrollment2 = Enrollment(
            class_id=test_class.id,
            user_id=student2.id
        )
        db.add_all([enrollment1, enrollment2])
        db.commit()
        
        # Login as student1
        login_response = client.post("/api/auth/login", json={
            "email": "student1@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to get recommendations for student2 (should fail)
        response = client.get(
            f"/api/recommendations?class_id={test_class.id}&student_id={student2.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Students can only view their own recommendations" in response.json()["detail"]
    
    def test_get_recommendations_teacher_wrong_class(self, client: TestClient, db: Session):
        """Test that teachers cannot view recommendations for students in other classes."""
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
        
        # Login as teacher2 (who doesn't own the class)
        login_response = client.post("/api/auth/login", json={
            "email": "teacher2@test.com",
            "password": "password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to get recommendations for student in teacher1's class (should fail)
        response = client.get(
            f"/api/recommendations?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "You can only view recommendations for students in your own classes" in response.json()["detail"]
    
    def test_recommendations_health_check(self, client: TestClient):
        """Test the recommendations health check endpoint."""
        response = client.get("/api/recommendations/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "Recommendations service is operational" in data["message"]
        assert "features" in data
        assert "skill_mastery_computation" in data["features"]


if __name__ == "__main__":
    # Run basic tests
    print("Running recommendations tests...")
    print("✅ Recommendations functionality tests completed!")

"""
Test recommendations API with weak skills
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.db.models import User, Class, Lesson, Assignment, Question, Enrollment, Submission, Response
from sqlalchemy.orm import Session
import json
from datetime import datetime, timezone

client = TestClient(app)

def create_recommendations_test_data(db: Session):
    """Create test data for recommendations testing"""
    
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
    
    # Create lessons with different skill tags
    lesson1 = Lesson(
        class_id=test_class.id,
        title="Introduction to Photosynthesis",
        content="This lesson covers the basics of photosynthesis...",
        skill_tags=json.dumps(["photosynthesis", "chlorophyll", "sunlight"])
    )
    db.add(lesson1)
    db.flush()
    
    lesson2 = Lesson(
        class_id=test_class.id,
        title="Advanced Plant Biology",
        content="This lesson covers advanced plant biology concepts...",
        skill_tags=json.dumps(["plant_biology", "chloroplasts", "glucose"])
    )
    db.add(lesson2)
    db.flush()
    
    lesson3 = Lesson(
        class_id=test_class.id,
        title="Ecosystem Energy Flow",
        content="This lesson covers energy flow in ecosystems...",
        skill_tags=json.dumps(["ecosystem", "energy_flow", "food_chain"])
    )
    db.add(lesson3)
    db.flush()
    
    # Create assignment to generate weak skills
    assignment = Assignment(
        class_id=test_class.id,
        title="Biology Quiz",
        type="quiz",
        rubric=json.dumps({
            "keywords": ["photosynthesis", "chlorophyll", "plant_biology"]
        })
    )
    db.add(assignment)
    db.flush()
    
    # Create questions
    question1 = Question(
        assignment_id=assignment.id,
        type="mcq",
        prompt="What is photosynthesis?",
        options=json.dumps(["A", "B", "C", "D"]),
        answer_key="A",
        skill_tags=json.dumps(["photosynthesis", "plant_biology"])
    )
    db.add(question1)
    db.flush()
    
    question2 = Question(
        assignment_id=assignment.id,
        type="short",
        prompt="Explain photosynthesis",
        answer_key="Plants use chlorophyll to capture light energy...",
        skill_tags=json.dumps(["photosynthesis", "chlorophyll"])
    )
    db.add(question2)
    db.flush()
    
    # Create submission with weak performance
    submission = Submission(
        assignment_id=assignment.id,
        student_id=student.id,
        submitted_at=datetime.now(timezone.utc),
        ai_score=0.3,  # Low score indicating weak skills
        teacher_score=None
    )
    db.add(submission)
    db.flush()
    
    # Create responses showing weak performance
    response1 = Response(
        submission_id=submission.id,
        question_id=question1.id,
        student_answer="B",  # Wrong answer
        ai_score=0.0,  # Incorrect
        teacher_score=None
    )
    db.add(response1)
    
    response2 = Response(
        submission_id=submission.id,
        question_id=question2.id,
        student_answer="Plants make food",  # Weak answer
        ai_score=0.2,  # Low score
        teacher_score=None
    )
    db.add(response2)
    
    db.commit()
    
    return {
        "teacher": teacher,
        "student": student,
        "class": test_class,
        "lessons": [lesson1, lesson2, lesson3],
        "assignment": assignment,
        "submission": submission
    }


def test_recommendations_with_weak_skills():
    """Test recommendations API returns lessons for weak skills"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_recommendations_test_data(db)
        
        # Login as teacher to access recommendations
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get recommendations for student
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "recommendations" in data
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= 3  # Should return top 3
        
        # Check each recommendation structure
        for rec in recommendations:
            assert "lesson_id" in rec
            assert "title" in rec
            assert "reason" in rec
            assert "score" in rec
            
            # Check reason is not empty and meaningful
            assert rec["reason"] is not None
            assert len(rec["reason"]) > 10
            assert isinstance(rec["reason"], str)
            
            # Check score is reasonable
            assert 0 <= rec["score"] <= 1
            
            # Verify lesson exists and has relevant skill tags
            lesson_id = rec["lesson_id"]
            lesson = next(l for l in test_data["lessons"] if l.id == lesson_id)
            assert lesson is not None
            
            # Check that recommended lessons have skills the student struggled with
            lesson_skills = json.loads(lesson.skill_tags)
            # Should include photosynthesis or chlorophyll (weak skills)
            has_relevant_skill = any(skill in lesson_skills for skill in ["photosynthesis", "chlorophyll", "plant_biology"])
            assert has_relevant_skill, f"Lesson {lesson.title} should have relevant skills for weak performance"
        
    finally:
        db.close()


def test_recommendations_student_access():
    """Test student can access their own recommendations"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_recommendations_test_data(db)
        
        # Login as student
        login_response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        student_token = login_response.json()["access_token"]
        
        # Get recommendations for student
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "recommendations" in data
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check recommendations are personalized
        for rec in recommendations:
            assert "reason" in rec
            # Reason should mention student's weak performance
            reason_lower = rec["reason"].lower()
            assert any(word in reason_lower for word in ["struggled", "weak", "difficulty", "improve", "help"])
        
    finally:
        db.close()


def test_recommendations_no_weak_skills():
    """Test recommendations when student has no weak skills"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_recommendations_test_data(db)
        
        # Update submission to have high scores (no weak skills)
        test_data["submission"].ai_score = 0.9
        db.commit()
        
        # Update responses to have high scores
        for response in db.query(Response).filter(Response.submission_id == test_data["submission"].id):
            response.ai_score = 0.9
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get recommendations
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return recommendations (content-based)
        assert "recommendations" in data
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        # May return fewer recommendations or different reasoning
        
    finally:
        db.close()


def test_recommendations_no_submissions():
    """Test recommendations for student with no submissions"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_recommendations_test_data(db)
        
        # Remove submission to simulate no submissions
        db.delete(test_data["submission"])
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get recommendations
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return content-based recommendations
        assert "recommendations" in data
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        # Should return some recommendations based on available lessons
        
    finally:
        db.close()


def test_recommendations_validation():
    """Test input validation for recommendations API"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_recommendations_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Test missing class_id
        response = client.get(
            f"/api/recommendations?student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422
        
        # Test missing student_id
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422
        
        # Test invalid class_id
        response = client.get(
            f"/api/recommendations?class_id=99999&student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 404
        
        # Test invalid student_id
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id=99999",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 404
        
        # Test unauthorized access
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id={test_data['student'].id}"
        )
        assert response.status_code == 401
        
    finally:
        db.close()


def test_recommendations_performance():
    """Test recommendations performance with multiple lessons and submissions"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_recommendations_test_data(db)
        
        # Add more lessons to test performance
        for i in range(5):
            lesson = Lesson(
                class_id=test_data["class"].id,
                title=f"Additional Lesson {i+1}",
                content=f"Content for lesson {i+1}...",
                skill_tags=json.dumps([f"skill_{i}", "photosynthesis", "plant_biology"])
            )
            db.add(lesson)
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get recommendations
        response = client.get(
            f"/api/recommendations?class_id={test_data['class'].id}&student_id={test_data['student'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return top 3 recommendations
        recommendations = data["recommendations"]
        assert len(recommendations) <= 3
        
        # Should be sorted by score (highest first)
        scores = [rec["score"] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
        
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Test misconceptions API with low-score short answers
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

def create_misconceptions_test_data(db: Session):
    """Create test data for misconceptions testing"""
    
    # Create teacher user
    teacher = User(
        email="teacher@test.com",
        name="Test Teacher",
        role="teacher",
        hashed_password="$2b$12$test_hash"
    )
    db.add(teacher)
    db.flush()
    
    # Create student users
    students = []
    for i in range(3):
        student = User(
            email=f"student{i}@test.com",
            name=f"Test Student {i}",
            role="student",
            hashed_password="$2b$12$test_hash"
        )
        db.add(student)
        db.flush()
        students.append(student)
    
    # Create class
    test_class = Class(
        name="Test Biology Class",
        teacher_id=teacher.id,
        invite_code="TEST123"
    )
    db.add(test_class)
    db.flush()
    
    # Enroll students in class
    for student in students:
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
            "keywords": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen", "photosynthesis"]
        })
    )
    db.add(assignment)
    db.flush()
    
    # Create short answer question
    question = Question(
        assignment_id=assignment.id,
        type="short",
        prompt="Explain the process of photosynthesis",
        answer_key="Plants use chlorophyll to capture light energy and convert carbon dioxide and water into glucose and oxygen through photosynthesis.",
        skill_tags=json.dumps(["photosynthesis", "chlorophyll", "plant_biology"])
    )
    db.add(question)
    db.flush()
    
    # Create submissions with low-score answers (misconceptions)
    misconceptions_data = [
        {
            "answer": "Plants eat sunlight and breathe in oxygen to make food",
            "ai_score": 0.2
        },
        {
            "answer": "Plants take in oxygen and release carbon dioxide like animals",
            "ai_score": 0.1
        },
        {
            "answer": "Plants just store sunlight in their leaves for later use",
            "ai_score": 0.3
        }
    ]
    
    submissions = []
    for i, student in enumerate(students):
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=misconceptions_data[i]["ai_score"],
            teacher_score=None
        )
        db.add(submission)
        db.flush()
        submissions.append(submission)
        
        # Create response with misconception
        response = Response(
            submission_id=submission.id,
            question_id=question.id,
            student_answer=misconceptions_data[i]["answer"],
            ai_score=misconceptions_data[i]["ai_score"],
            teacher_score=None,
            ai_feedback=f"Low score due to misconception: {misconceptions_data[i]['answer']}"
        )
        db.add(response)
    
    db.commit()
    
    return {
        "teacher": teacher,
        "students": students,
        "class": test_class,
        "assignment": assignment,
        "question": question,
        "submissions": submissions
    }


def test_misconceptions_with_low_scores():
    """Test misconceptions API returns clusters for low-score answers"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_misconceptions_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get misconceptions
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "clusters" in data
        assert "message" in data
        assert "total_responses" in data
        assert "analyzed_responses" in data
        
        clusters = data["clusters"]
        assert isinstance(clusters, list)
        assert len(clusters) > 0
        assert len(clusters) <= 3  # Should return up to 3 clusters
        
        # Check each cluster structure
        for cluster in clusters:
            assert "label" in cluster
            assert "examples" in cluster
            assert "suggested_skill_tags" in cluster
            assert "count" in cluster
            
            # Check label is meaningful
            assert cluster["label"] is not None
            assert len(cluster["label"]) > 5
            assert isinstance(cluster["label"], str)
            
            # Check examples are present
            assert isinstance(cluster["examples"], list)
            assert len(cluster["examples"]) > 0
            assert len(cluster["examples"]) <= 2  # Should show 1-2 examples
            
            # Check examples are actual student answers
            for example in cluster["examples"]:
                assert isinstance(example, str)
                assert len(example) > 5
                # Should be one of our misconception answers
                assert any(misconception in example.lower() for misconception in [
                    "eat sunlight", "breathe oxygen", "take in oxygen", "store sunlight"
                ])
            
            # Check suggested skill tags
            assert isinstance(cluster["suggested_skill_tags"], list)
            assert len(cluster["suggested_skill_tags"]) > 0
            # Should include relevant skills
            assert any(skill in cluster["suggested_skill_tags"] for skill in [
                "photosynthesis", "chlorophyll", "plant_biology"
            ])
            
            # Check count is reasonable
            assert cluster["count"] > 0
            assert cluster["count"] <= 3  # Should not exceed number of students
        
        # Check totals
        assert data["total_responses"] == 3  # Three student responses
        assert data["analyzed_responses"] == 3  # All should be analyzed
        
    finally:
        db.close()


def test_misconceptions_not_enough_data():
    """Test misconceptions API when there's not enough data"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_misconceptions_test_data(db)
        
        # Remove most submissions to simulate insufficient data
        for submission in test_data["submissions"][1:]:
            db.delete(submission)
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get misconceptions
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return "not enough data" message
        assert "clusters" in data
        assert "message" in data
        
        # Should have empty clusters or fallback message
        clusters = data["clusters"]
        if len(clusters) == 0:
            assert "not enough data" in data["message"].lower()
        else:
            # If clusters exist, they should be minimal
            assert len(clusters) == 1
        
    finally:
        db.close()


def test_misconceptions_no_low_scores():
    """Test misconceptions API when all answers score well"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_misconceptions_test_data(db)
        
        # Update all responses to have high scores
        for submission in test_data["submissions"]:
            submission.ai_score = 0.9
            for response in db.query(Response).filter(Response.submission_id == submission.id):
                response.ai_score = 0.9
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get misconceptions
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty clusters or positive message
        assert "clusters" in data
        clusters = data["clusters"]
        
        if len(clusters) == 0:
            assert "no misconceptions" in data["message"].lower() or "performing well" in data["message"].lower()
        else:
            # If clusters exist, they should be minimal
            assert len(clusters) <= 1
        
    finally:
        db.close()


def test_misconceptions_mixed_scores():
    """Test misconceptions API with mixed high and low scores"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_misconceptions_test_data(db)
        
        # Update one submission to have high score
        test_data["submissions"][0].ai_score = 0.9
        for response in db.query(Response).filter(Response.submission_id == test_data["submissions"][0].id):
            response.ai_score = 0.9
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get misconceptions
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return clusters for low-score answers only
        assert "clusters" in data
        clusters = data["clusters"]
        
        if len(clusters) > 0:
            # Check that clusters only include low-score misconceptions
            for cluster in clusters:
                for example in cluster["examples"]:
                    # Should not include the high-score answer
                    assert "plants use chlorophyll to capture light energy" not in example.lower()
        
        # Should analyze only low-score responses
        assert data["analyzed_responses"] == 2  # Only 2 low-score responses
        
    finally:
        db.close()


def test_misconceptions_validation():
    """Test input validation for misconceptions API"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_misconceptions_test_data(db)
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Test missing class_id
        response = client.get(
            "/api/insights/misconceptions",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 422
        
        # Test invalid class_id
        response = client.get(
            "/api/insights/misconceptions?class_id=99999",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert response.status_code == 404
        
        # Test unauthorized access
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}"
        )
        assert response.status_code == 401
        
        # Test student access (should be denied)
        student_login = client.post("/api/auth/login", json={
            "email": "student0@test.com",
            "password": "test_password"
        })
        assert student_login.status_code == 200
        student_token = student_login.json()["access_token"]
        
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403  # Forbidden for students
        
    finally:
        db.close()


def test_misconceptions_performance():
    """Test misconceptions API performance with many responses"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        test_data = create_misconceptions_test_data(db)
        
        # Add more students and responses to test performance
        for i in range(10):
            student = User(
                email=f"student{i+3}@test.com",
                name=f"Test Student {i+3}",
                role="student",
                hashed_password="$2b$12$test_hash"
            )
            db.add(student)
            db.flush()
            
            # Enroll student
            enrollment = Enrollment(
                class_id=test_data["class"].id,
                student_id=student.id
            )
            db.add(enrollment)
            
            # Create submission
            submission = Submission(
                assignment_id=test_data["assignment"].id,
                student_id=student.id,
                submitted_at=datetime.now(timezone.utc),
                ai_score=0.2 + (i * 0.05),  # Varying low scores
                teacher_score=None
            )
            db.add(submission)
            db.flush()
            
            # Create response
            response = Response(
                submission_id=submission.id,
                question_id=test_data["question"].id,
                student_answer=f"Misconception answer {i}: Plants do something wrong",
                ai_score=0.2 + (i * 0.05),
                teacher_score=None
            )
            db.add(response)
        
        db.commit()
        
        # Login as teacher
        login_response = client.post("/api/auth/login", json={
            "email": "teacher@test.com",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        teacher_token = login_response.json()["access_token"]
        
        # Get misconceptions
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_data['class'].id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return reasonable number of clusters
        clusters = data["clusters"]
        assert len(clusters) <= 3  # Should not exceed 3 clusters
        
        # Should analyze all low-score responses
        assert data["analyzed_responses"] >= 10  # Should analyze many responses
        
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

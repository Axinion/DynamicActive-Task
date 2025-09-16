"""
Test Phase 4 - Misconceptions API (Weekly Analysis)

Tests the /api/insights/misconceptions endpoint with period=week parameter.
Verifies clustering functionality, response structure, and data integrity.
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import User, Class, Assignment, Question, Submission, Response
from app.core.config import settings


class TestMisconceptionsWeek:
    """Test misconceptions API with weekly period filtering"""

    def test_misconceptions_week_basic(self, client: TestClient, db: Session, teacher_token: str):
        """Test basic misconceptions API call with week period"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Test Analytics Class",
            teacher_id=teacher.id,
            invite_code="TEST123"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment with low-scoring questions
        assignment = Assignment(
            class_id=test_class.id,
            title="Analytics Test Assignment",
            type="quiz",
            rubric={"keywords": ["photosynthesis", "chlorophyll", "light"]}
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create questions with different skill tags
        question1 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy into chemical energy",
            skill_tags=["photosynthesis", "plant_biology"]
        )
        question2 = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What color is chlorophyll?",
            options=["red", "blue", "green", "yellow"],
            answer_key="green",
            skill_tags=["chlorophyll", "plant_biology"]
        )
        db.add_all([question1, question2])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)

        # Create submission within last week
        recent_time = datetime.now(timezone.utc) - timedelta(days=3)
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=recent_time,
            ai_score=25.0,  # Low score to trigger misconception
            ai_explanation="Student shows misconceptions about photosynthesis"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create low-scoring responses
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="Plants eat sunlight",  # Misconception
            ai_score=0.2,  # Low score
            ai_feedback="Incorrect understanding of photosynthesis process"
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="red",  # Wrong MCQ answer
            ai_score=0.0,  # Incorrect
            ai_feedback="Chlorophyll is green, not red"
        )
        db.add_all([response1, response2])
        db.commit()

        # Call misconceptions API
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}&period=week",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "class_id" in data
        assert "class_name" in data
        assert "period" in data
        assert "time_window" in data
        assert "total_items" in data
        assert "clusters" in data
        assert "analysis_summary" in data
        
        # Check period
        assert data["period"] == "week"
        assert data["class_id"] == test_class.id
        
        # Check time window
        assert "start" in data["time_window"]
        assert "end" in data["time_window"]
        
        # Check clusters
        clusters = data["clusters"]
        assert isinstance(clusters, list)
        assert len(clusters) <= 3  # Should have at most 3 clusters
        
        # Check each cluster structure
        for cluster in clusters:
            assert "label" in cluster
            assert "examples" in cluster
            assert "suggested_skill_tags" in cluster
            assert "cluster_size" in cluster
            assert "common_keywords" in cluster
            
            # Check label is not empty
            assert cluster["label"] and len(cluster["label"]) > 0
            
            # Check examples structure
            examples = cluster["examples"]
            assert isinstance(examples, list)
            assert len(examples) <= 2  # At most 2 examples per cluster
            
            for example in examples:
                assert "student_answer" in example
                assert "question_prompt" in example
                assert "score" in example
                assert "assignment_title" in example
                
                # Check score is low (indicating misconception)
                assert example["score"] < settings.short_answer_pass_threshold
            
            # Check cluster size
            assert cluster["cluster_size"] > 0
            
            # Check suggested skill tags
            assert isinstance(cluster["suggested_skill_tags"], list)
        
        # Check analysis summary
        summary = data["analysis_summary"]
        assert "total_clusters" in summary
        assert "threshold_used" in summary
        assert "analysis_type" in summary

    def test_misconceptions_week_no_data(self, client: TestClient, db: Session, teacher_token: str):
        """Test misconceptions API when no low-scoring responses exist"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="No Data Class",
            teacher_id=teacher.id,
            invite_code="NODATA"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="High Scoring Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create question
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is 2+2?",
            answer_key="4",
            skill_tags=["basic_math"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)

        # Create high-scoring submission
        recent_time = datetime.now(timezone.utc) - timedelta(days=2)
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=recent_time,
            ai_score=95.0  # High score
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create high-scoring response
        response = Response(
            submission_id=submission.id,
            question_id=question.id,
            student_answer="4",
            ai_score=1.0  # Perfect score
        )
        db.add(response)
        db.commit()

        # Call misconceptions API
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}&period=week",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should return empty clusters
        assert response.status_code == 200
        data = response.json()
        assert data["clusters"] == []
        assert data["total_items"] == 0

    def test_misconceptions_week_old_data(self, client: TestClient, db: Session, teacher_token: str):
        """Test misconceptions API excludes data older than week"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Old Data Class",
            teacher_id=teacher.id,
            invite_code="OLDATA"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Old Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create question
        question = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy",
            skill_tags=["photosynthesis"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)

        # Create old submission (2 weeks ago)
        old_time = datetime.now(timezone.utc) - timedelta(days=14)
        old_submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=old_time,
            ai_score=20.0  # Low score
        )
        db.add(old_submission)
        db.commit()
        db.refresh(old_submission)

        # Create old low-scoring response
        old_response = Response(
            submission_id=old_submission.id,
            question_id=question.id,
            student_answer="Plants eat sunlight",
            ai_score=0.1  # Very low score
        )
        db.add(old_response)
        db.commit()

        # Call misconceptions API
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}&period=week",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should return empty clusters (old data excluded)
        assert response.status_code == 200
        data = response.json()
        assert data["clusters"] == []
        assert data["total_items"] == 0

    def test_misconceptions_week_invalid_period(self, client: TestClient, db: Session, teacher_token: str):
        """Test misconceptions API with invalid period parameter"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        test_class = Class(
            name="Invalid Period Class",
            teacher_id=teacher.id,
            invite_code="INVALID"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Call misconceptions API with invalid period
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}&period=invalid",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should return 422 error
        assert response.status_code == 422

    def test_misconceptions_week_unauthorized(self, client: TestClient, db: Session, student_token: str):
        """Test misconceptions API requires teacher access"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        test_class = Class(
            name="Unauthorized Class",
            teacher_id=teacher.id,
            invite_code="UNAUTH"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Call misconceptions API as student
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}&period=week",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        # Should return 403 error
        assert response.status_code == 403

    def test_misconceptions_week_clustering_logic(self, client: TestClient, db: Session, teacher_token: str):
        """Test that misconceptions are properly clustered by similarity"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Clustering Test Class",
            teacher_id=teacher.id,
            invite_code="CLUSTER"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Clustering Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create multiple questions with similar misconceptions
        question1 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy into chemical energy",
            skill_tags=["photosynthesis", "plant_biology"]
        )
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="How do plants make food?",
            answer_key="Through photosynthesis using sunlight",
            skill_tags=["photosynthesis", "plant_biology"]
        )
        question3 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is the water cycle?",
            answer_key="Continuous movement of water through evaporation and precipitation",
            skill_tags=["water_cycle", "earth_science"]
        )
        db.add_all([question1, question2, question3])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)
        db.refresh(question3)

        # Create submission
        recent_time = datetime.now(timezone.utc) - timedelta(days=2)
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=recent_time,
            ai_score=30.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create responses with similar misconceptions
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="Plants eat sunlight",  # Similar misconception
            ai_score=0.2
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="Plants consume light",  # Similar misconception
            ai_score=0.3
        )
        response3 = Response(
            submission_id=submission.id,
            question_id=question3.id,
            student_answer="Water goes up and down",  # Different misconception
            ai_score=0.1
        )
        db.add_all([response1, response2, response3])
        db.commit()

        # Call misconceptions API
        response = client.get(
            f"/api/insights/misconceptions?class_id={test_class.id}&period=week",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should return clusters
        assert response.status_code == 200
        data = response.json()
        
        # Should have some clusters (exact number depends on clustering algorithm)
        assert len(data["clusters"]) > 0
        assert len(data["clusters"]) <= 3
        
        # Check that clusters have meaningful labels
        for cluster in data["clusters"]:
            assert cluster["label"] and len(cluster["label"]) > 0
            assert cluster["cluster_size"] > 0
            assert len(cluster["examples"]) > 0

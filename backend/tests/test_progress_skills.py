"""
Test Phase 4 - Student Progress Skills API

Tests the /api/progress/skills endpoint for skill mastery computation.
Verifies mastery calculation, ordering, and response structure.
"""

import pytest
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import User, Class, Assignment, Question, Submission, Response


class TestProgressSkills:
    """Test student progress skills API"""

    def test_progress_skills_basic(self, client: TestClient, db: Session, teacher_token: str, student_token: str):
        """Test basic progress skills API call"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Progress Test Class",
            teacher_id=teacher.id,
            invite_code="PROGRESS"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignments
        assignment1 = Assignment(
            class_id=test_class.id,
            title="Math Assignment",
            type="quiz"
        )
        assignment2 = Assignment(
            class_id=test_class.id,
            title="Science Assignment",
            type="quiz"
        )
        db.add_all([assignment1, assignment2])
        db.commit()
        db.refresh(assignment1)
        db.refresh(assignment2)

        # Create questions with different skill tags
        question1 = Question(
            assignment_id=assignment1.id,
            type="short",
            prompt="What is 2+2?",
            answer_key="4",
            skill_tags=["basic_math", "arithmetic"]
        )
        question2 = Question(
            assignment_id=assignment1.id,
            type="mcq",
            prompt="What is 5*3?",
            options=["10", "15", "20", "25"],
            answer_key="15",
            skill_tags=["basic_math", "multiplication"]
        )
        question3 = Question(
            assignment_id=assignment2.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy",
            skill_tags=["photosynthesis", "plant_biology"]
        )
        db.add_all([question1, question2, question3])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)
        db.refresh(question3)

        # Create submissions
        submission1 = Submission(
            assignment_id=assignment1.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=80.0
        )
        submission2 = Submission(
            assignment_id=assignment2.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=60.0
        )
        db.add_all([submission1, submission2])
        db.commit()
        db.refresh(submission1)
        db.refresh(submission2)

        # Create responses with different scores
        response1 = Response(
            submission_id=submission1.id,
            question_id=question1.id,
            student_answer="4",
            ai_score=1.0  # Perfect score
        )
        response2 = Response(
            submission_id=submission1.id,
            question_id=question2.id,
            student_answer="15",
            ai_score=1.0  # Perfect score
        )
        response3 = Response(
            submission_id=submission2.id,
            question_id=question3.id,
            student_answer="Plants make food from sunlight",
            ai_score=0.6  # Partial score
        )
        db.add_all([response1, response2, response3])
        db.commit()

        # Call progress skills API as teacher
        response = client.get(
            f"/api/progress/skills?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "skill_mastery" in data
        assert "overall_mastery_avg" in data
        assert "total_responses" in data
        assert "skills_analyzed" in data
        assert "student" in data
        assert "class_id" in data
        assert "requested_by" in data
        assert "analysis_summary" in data
        
        # Check student info
        assert data["student"]["id"] == student.id
        assert data["student"]["name"] == student.name
        assert data["student"]["email"] == student.email
        
        # Check class info
        assert data["class_id"] == test_class.id
        
        # Check requested by info
        assert data["requested_by"]["id"] == teacher.id
        assert data["requested_by"]["role"] == "teacher"
        
        # Check skill mastery
        skill_mastery = data["skill_mastery"]
        assert isinstance(skill_mastery, list)
        assert len(skill_mastery) > 0
        
        # Check each skill mastery entry
        for skill in skill_mastery:
            assert "tag" in skill
            assert "mastery" in skill
            assert "samples" in skill
            assert "responses" in skill
            
            # Check mastery is between 0 and 1
            assert 0 <= skill["mastery"] <= 1
            
            # Check samples count
            assert skill["samples"] > 0
            
            # Check responses structure
            responses = skill["responses"]
            assert isinstance(responses, list)
            assert len(responses) == skill["samples"]
            
            for resp in responses:
                assert "score" in resp
                assert "question_id" in resp
                assert "question_type" in resp
                assert "assignment_id" in resp
                assert "assignment_title" in resp
                
                # Check score is between 0 and 1
                assert 0 <= resp["score"] <= 1
        
        # Check overall mastery
        assert 0 <= data["overall_mastery_avg"] <= 1
        
        # Check total responses
        assert data["total_responses"] == 3
        
        # Check skills analyzed
        assert data["skills_analyzed"] == len(skill_mastery)
        
        # Check analysis summary
        summary = data["analysis_summary"]
        assert "mcq_scoring" in summary
        assert "short_answer_scoring" in summary
        assert "mastery_calculation" in summary

    def test_progress_skills_student_access(self, client: TestClient, db: Session, student_token: str):
        """Test student can access their own progress"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Student Access Class",
            teacher_id=teacher.id,
            invite_code="STUDENT"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Student Test Assignment",
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

        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=80.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create response
        response = Response(
            submission_id=submission.id,
            question_id=question.id,
            student_answer="4",
            ai_score=1.0
        )
        db.add(response)
        db.commit()

        # Call progress skills API as student
        response = client.get(
            f"/api/progress/skills?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["student"]["id"] == student.id
        assert data["requested_by"]["id"] == student.id
        assert data["requested_by"]["role"] == "student"

    def test_progress_skills_unauthorized_student(self, client: TestClient, db: Session, student_token: str):
        """Test student cannot access another student's progress"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student1 = db.query(User).filter(User.role == "student").first()
        
        # Create another student
        student2 = User(
            name="Another Student",
            email="another@student.com",
            role="student",
            hashed_password="hashed"
        )
        db.add(student2)
        db.commit()
        db.refresh(student2)
        
        # Create class
        test_class = Class(
            name="Unauthorized Class",
            teacher_id=teacher.id,
            invite_code="UNAUTH"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Try to access another student's progress
        response = client.get(
            f"/api/progress/skills?class_id={test_class.id}&student_id={student2.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        # Should return 403 error
        assert response.status_code == 403

    def test_progress_skills_mastery_calculation(self, client: TestClient, db: Session, teacher_token: str):
        """Test mastery calculation for different skill tags"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Mastery Calculation Class",
            teacher_id=teacher.id,
            invite_code="MASTERY"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Mastery Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create questions with specific skill tags
        question1 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is 2+2?",
            answer_key="4",
            skill_tags=["arithmetic"]  # Tag A
        )
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is 3+3?",
            answer_key="6",
            skill_tags=["arithmetic"]  # Tag A
        )
        question3 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy",
            skill_tags=["photosynthesis"]  # Tag B
        )
        question4 = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What is 4*4?",
            options=["12", "16", "20", "24"],
            answer_key="16",
            skill_tags=["multiplication"]  # Tag C
        )
        db.add_all([question1, question2, question3, question4])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)
        db.refresh(question3)
        db.refresh(question4)

        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=75.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create responses with specific scores
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="4",
            ai_score=1.0  # Perfect for arithmetic
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="6",
            ai_score=1.0  # Perfect for arithmetic
        )
        response3 = Response(
            submission_id=submission.id,
            question_id=question3.id,
            student_answer="Plants make food",
            ai_score=0.5  # Partial for photosynthesis
        )
        response4 = Response(
            submission_id=submission.id,
            question_id=question4.id,
            student_answer="16",
            ai_score=1.0  # Perfect for multiplication
        )
        db.add_all([response1, response2, response3, response4])
        db.commit()

        # Call progress skills API
        response = client.get(
            f"/api/progress/skills?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        
        # Check skill mastery
        skill_mastery = data["skill_mastery"]
        assert len(skill_mastery) == 3  # Should have 3 different skills
        
        # Find each skill and check mastery
        arithmetic_skill = next((s for s in skill_mastery if s["tag"] == "arithmetic"), None)
        photosynthesis_skill = next((s for s in skill_mastery if s["tag"] == "photosynthesis"), None)
        multiplication_skill = next((s for s in skill_mastery if s["tag"] == "multiplication"), None)
        
        assert arithmetic_skill is not None
        assert photosynthesis_skill is not None
        assert multiplication_skill is not None
        
        # Check mastery calculations
        assert arithmetic_skill["mastery"] == 1.0  # (1.0 + 1.0) / 2 = 1.0
        assert arithmetic_skill["samples"] == 2
        
        assert photosynthesis_skill["mastery"] == 0.5  # 0.5 / 1 = 0.5
        assert photosynthesis_skill["samples"] == 1
        
        assert multiplication_skill["mastery"] == 1.0  # 1.0 / 1 = 1.0
        assert multiplication_skill["samples"] == 1
        
        # Check overall mastery
        expected_overall = (1.0 + 1.0 + 0.5 + 1.0) / 4  # 0.875
        assert abs(data["overall_mastery_avg"] - expected_overall) < 0.001

    def test_progress_skills_ordering(self, client: TestClient, db: Session, teacher_token: str):
        """Test that skills are ordered by mastery (lowest first)"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Ordering Test Class",
            teacher_id=teacher.id,
            invite_code="ORDERING"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Ordering Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create questions with different skill tags
        question1 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is 2+2?",
            answer_key="4",
            skill_tags=["arithmetic"]
        )
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy",
            skill_tags=["photosynthesis"]
        )
        question3 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is gravity?",
            answer_key="Force that attracts objects to each other",
            skill_tags=["physics"]
        )
        db.add_all([question1, question2, question3])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)
        db.refresh(question3)

        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=60.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create responses with different scores
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="4",
            ai_score=1.0  # High mastery
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="Plants make food",
            ai_score=0.3  # Low mastery
        )
        response3 = Response(
            submission_id=submission.id,
            question_id=question3.id,
            student_answer="Force that pulls things down",
            ai_score=0.7  # Medium mastery
        )
        db.add_all([response1, response2, response3])
        db.commit()

        # Call progress skills API
        response = client.get(
            f"/api/progress/skills?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        
        # Check skill mastery ordering
        skill_mastery = data["skill_mastery"]
        assert len(skill_mastery) == 3
        
        # Skills should be ordered by mastery (lowest first)
        assert skill_mastery[0]["mastery"] <= skill_mastery[1]["mastery"]
        assert skill_mastery[1]["mastery"] <= skill_mastery[2]["mastery"]
        
        # Check specific ordering
        assert skill_mastery[0]["tag"] == "photosynthesis"  # 0.3
        assert skill_mastery[1]["tag"] == "physics"  # 0.7
        assert skill_mastery[2]["tag"] == "arithmetic"  # 1.0

    def test_progress_skills_no_data(self, client: TestClient, db: Session, teacher_token: str):
        """Test progress skills API when no responses exist"""
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

        # Call progress skills API
        response = client.get(
            f"/api/progress/skills?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed but return empty data
        assert response.status_code == 200
        data = response.json()
        
        assert data["skill_mastery"] == []
        assert data["overall_mastery_avg"] == 0.0
        assert data["total_responses"] == 0
        assert data["skills_analyzed"] == 0

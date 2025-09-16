"""
Test Phase 4 - Mini-Lessons Suggestions API

Tests the /api/suggestions/mini-lessons endpoints.
Verifies lesson suggestions, tag matching, and response structure.
"""

import pytest
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import User, Class, Lesson, Assignment, Question, Submission, Response


class TestMiniLessons:
    """Test mini-lessons suggestions API"""

    def test_mini_lessons_basic(self, client: TestClient, db: Session, teacher_token: str):
        """Test basic mini-lessons API call"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="Mini-Lessons Test Class",
            teacher_id=teacher.id,
            invite_code="MINILESSONS"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create lessons with different skill tags
        lesson1 = Lesson(
            class_id=test_class.id,
            title="Introduction to Photosynthesis",
            content="Photosynthesis is the process by which plants convert light energy into chemical energy...",
            skill_tags=["photosynthesis", "plant_biology"]
        )
        lesson2 = Lesson(
            class_id=test_class.id,
            title="Advanced Photosynthesis Concepts",
            content="Chlorophyll and light absorption in photosynthesis...",
            skill_tags=["photosynthesis", "chlorophyll"]
        )
        lesson3 = Lesson(
            class_id=test_class.id,
            title="Basic Math Operations",
            content="Addition, subtraction, multiplication, and division...",
            skill_tags=["arithmetic", "basic_math"]
        )
        lesson4 = Lesson(
            class_id=test_class.id,
            title="Water Cycle Explained",
            content="The water cycle is the continuous movement of water...",
            skill_tags=["water_cycle", "earth_science"]
        )
        db.add_all([lesson1, lesson2, lesson3, lesson4])
        db.commit()
        db.refresh(lesson1)
        db.refresh(lesson2)
        db.refresh(lesson3)
        db.refresh(lesson4)

        # Call mini-lessons API
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=photosynthesis,arithmetic",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "class_id" in data
        assert "class_name" in data
        assert "requested_tags" in data
        assert "suggestions" in data
        assert "requested_by" in data
        
        # Check class info
        assert data["class_id"] == test_class.id
        assert data["class_name"] == test_class.name
        
        # Check requested tags
        assert data["requested_tags"] == ["photosynthesis", "arithmetic"]
        
        # Check requested by info
        assert data["requested_by"]["id"] == teacher.id
        assert data["requested_by"]["role"] == "teacher"
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert isinstance(suggestions, list)
        assert len(suggestions) == 2  # Should have suggestions for both tags
        
        # Check each suggestion
        for suggestion in suggestions:
            assert "tag" in suggestion
            assert "lessons" in suggestion
            assert "total_matches" in suggestion
            assert "exact_matches" in suggestion
            
            # Check tag is one of the requested tags
            assert suggestion["tag"] in ["photosynthesis", "arithmetic"]
            
            # Check lessons structure
            lessons = suggestion["lessons"]
            assert isinstance(lessons, list)
            assert len(lessons) <= 3  # At most 3 lessons per tag
            
            for lesson in lessons:
                assert "lesson_id" in lesson
                assert "title" in lesson
                
                # Check lesson exists in database
                db_lesson = db.query(Lesson).filter(Lesson.id == lesson["lesson_id"]).first()
                assert db_lesson is not None
                assert db_lesson.title == lesson["title"]
            
            # Check match counts
            assert suggestion["total_matches"] >= 0
            assert suggestion["exact_matches"] >= 0
            assert suggestion["exact_matches"] <= suggestion["total_matches"]

    def test_mini_lessons_exact_match_priority(self, client: TestClient, db: Session, teacher_token: str):
        """Test that exact tag matches are prioritized over partial matches"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="Exact Match Test Class",
            teacher_id=teacher.id,
            invite_code="EXACTMATCH"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create lessons with exact and partial tag matches
        lesson1 = Lesson(
            class_id=test_class.id,
            title="Exact Photosynthesis Match",
            content="Exact match for photosynthesis tag...",
            skill_tags=["photosynthesis"]  # Exact match
        )
        lesson2 = Lesson(
            class_id=test_class.id,
            title="Partial Photosynthesis Match",
            content="Partial match for photosynthesis tag...",
            skill_tags=["photosynthesis_advanced"]  # Partial match
        )
        lesson3 = Lesson(
            class_id=test_class.id,
            title="Another Exact Match",
            content="Another exact match for photosynthesis...",
            skill_tags=["photosynthesis", "plant_biology"]  # Exact match
        )
        db.add_all([lesson1, lesson2, lesson3])
        db.commit()
        db.refresh(lesson1)
        db.refresh(lesson2)
        db.refresh(lesson3)

        # Call mini-lessons API
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=photosynthesis",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert len(suggestions) == 1
        assert suggestions[0]["tag"] == "photosynthesis"
        
        # Check that exact matches are prioritized
        lessons = suggestions[0]["lessons"]
        assert len(lessons) >= 2  # Should have at least 2 lessons
        
        # First lessons should be exact matches
        exact_match_lessons = [l for l in lessons if l["title"] in ["Exact Photosynthesis Match", "Another Exact Match"]]
        assert len(exact_match_lessons) >= 2
        
        # Check match counts
        assert suggestions[0]["exact_matches"] >= 2
        assert suggestions[0]["total_matches"] >= 2

    def test_mini_lessons_recency_ordering(self, client: TestClient, db: Session, teacher_token: str):
        """Test that lessons are ordered by recency (newest first)"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="Recency Test Class",
            teacher_id=teacher.id,
            invite_code="RECENCY"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create lessons with different creation times
        base_time = datetime.now(timezone.utc)
        
        lesson1 = Lesson(
            class_id=test_class.id,
            title="Oldest Lesson",
            content="This is the oldest lesson...",
            skill_tags=["photosynthesis"],
            created_at=base_time
        )
        lesson2 = Lesson(
            class_id=test_class.id,
            title="Newest Lesson",
            content="This is the newest lesson...",
            skill_tags=["photosynthesis"],
            created_at=base_time.replace(day=base_time.day + 1)
        )
        lesson3 = Lesson(
            class_id=test_class.id,
            title="Middle Lesson",
            content="This is the middle lesson...",
            skill_tags=["photosynthesis"],
            created_at=base_time.replace(hour=base_time.hour + 1)
        )
        db.add_all([lesson1, lesson2, lesson3])
        db.commit()
        db.refresh(lesson1)
        db.refresh(lesson2)
        db.refresh(lesson3)

        # Call mini-lessons API
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=photosynthesis",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert len(suggestions) == 1
        assert suggestions[0]["tag"] == "photosynthesis"
        
        # Check that lessons are ordered by recency
        lessons = suggestions[0]["lessons"]
        assert len(lessons) == 3
        
        # First lesson should be the newest
        assert lessons[0]["title"] == "Newest Lesson"
        
        # Last lesson should be the oldest
        assert lessons[2]["title"] == "Oldest Lesson"

    def test_mini_lessons_weak_skills(self, client: TestClient, db: Session, teacher_token: str):
        """Test mini-lessons for weak skills endpoint"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        student = db.query(User).filter(User.role == "student").first()
        
        # Create class
        test_class = Class(
            name="Weak Skills Test Class",
            teacher_id=teacher.id,
            invite_code="WEAKSKILLS"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create lessons for weak skills
        lesson1 = Lesson(
            class_id=test_class.id,
            title="Photosynthesis Basics",
            content="Learn the basics of photosynthesis...",
            skill_tags=["photosynthesis", "plant_biology"]
        )
        lesson2 = Lesson(
            class_id=test_class.id,
            title="Advanced Photosynthesis",
            content="Advanced concepts in photosynthesis...",
            skill_tags=["photosynthesis", "chlorophyll"]
        )
        lesson3 = Lesson(
            class_id=test_class.id,
            title="Math Fundamentals",
            content="Basic math concepts...",
            skill_tags=["arithmetic", "basic_math"]
        )
        db.add_all([lesson1, lesson2, lesson3])
        db.commit()
        db.refresh(lesson1)
        db.refresh(lesson2)
        db.refresh(lesson3)

        # Create assignment
        assignment = Assignment(
            class_id=test_class.id,
            title="Weak Skills Test Assignment",
            type="quiz"
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        # Create questions
        question1 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is photosynthesis?",
            answer_key="Process by which plants convert light energy",
            skill_tags=["photosynthesis"]
        )
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="What is 2+2?",
            answer_key="4",
            skill_tags=["arithmetic"]
        )
        db.add_all([question1, question2])
        db.commit()
        db.refresh(question1)
        db.refresh(question2)

        # Create submission
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submitted_at=datetime.now(timezone.utc),
            ai_score=40.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Create responses with low scores (weak skills)
        response1 = Response(
            submission_id=submission.id,
            question_id=question1.id,
            student_answer="Plants eat sunlight",
            ai_score=0.2  # Low score for photosynthesis
        )
        response2 = Response(
            submission_id=submission.id,
            question_id=question2.id,
            student_answer="3",
            ai_score=0.1  # Low score for arithmetic
        )
        db.add_all([response1, response2])
        db.commit()

        # Call mini-lessons for weak skills API
        response = client.get(
            f"/api/suggestions/mini-lessons/weak-skills?class_id={test_class.id}&student_id={student.id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "class_id" in data
        assert "student_id" in data
        assert "student_name" in data
        assert "weak_skills" in data
        assert "suggestions" in data
        assert "requested_by" in data
        
        # Check student info
        assert data["student_id"] == student.id
        assert data["student_name"] == student.name
        
        # Check weak skills
        weak_skills = data["weak_skills"]
        assert isinstance(weak_skills, list)
        assert len(weak_skills) == 2  # Should have 2 weak skills
        
        # Check each weak skill
        for skill in weak_skills:
            assert "tag" in skill
            assert "mastery" in skill
            assert "samples" in skill
            
            # Check mastery is low (weak skill)
            assert skill["mastery"] < 0.6
            
            # Check samples count
            assert skill["samples"] == 1
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert isinstance(suggestions, list)
        assert len(suggestions) == 2  # Should have suggestions for both weak skills
        
        # Check each suggestion
        for suggestion in suggestions:
            assert "tag" in suggestion
            assert "mastery" in suggestion
            assert "samples" in suggestion
            assert "lessons" in suggestion
            
            # Check tag is one of the weak skills
            assert suggestion["tag"] in ["photosynthesis", "arithmetic"]
            
            # Check mastery is low
            assert suggestion["mastery"] < 0.6
            
            # Check lessons are provided
            lessons = suggestion["lessons"]
            assert isinstance(lessons, list)
            assert len(lessons) > 0
            
            for lesson in lessons:
                assert "lesson_id" in lesson
                assert "title" in lesson
                
                # Check lesson exists in database
                db_lesson = db.query(Lesson).filter(Lesson.id == lesson["lesson_id"]).first()
                assert db_lesson is not None
                assert db_lesson.title == lesson["title"]

    def test_mini_lessons_unauthorized(self, client: TestClient, db: Session, student_token: str):
        """Test mini-lessons API requires teacher access"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="Unauthorized Class",
            teacher_id=teacher.id,
            invite_code="UNAUTH"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Call mini-lessons API as student
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=photosynthesis",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        # Should return 403 error
        assert response.status_code == 403

    def test_mini_lessons_no_lessons(self, client: TestClient, db: Session, teacher_token: str):
        """Test mini-lessons API when no lessons exist for requested tags"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="No Lessons Class",
            teacher_id=teacher.id,
            invite_code="NOLESSONS"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create lesson with different tags
        lesson = Lesson(
            class_id=test_class.id,
            title="Unrelated Lesson",
            content="This lesson is not related to the requested tags...",
            skill_tags=["unrelated_tag"]
        )
        db.add(lesson)
        db.commit()

        # Call mini-lessons API
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=photosynthesis,arithmetic",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed but return empty suggestions
        assert response.status_code == 200
        data = response.json()
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert len(suggestions) == 2  # Should have suggestions for both tags
        
        # Check that both suggestions have no lessons
        for suggestion in suggestions:
            assert suggestion["tag"] in ["photosynthesis", "arithmetic"]
            assert suggestion["lessons"] == []
            assert suggestion["total_matches"] == 0
            assert suggestion["exact_matches"] == 0

    def test_mini_lessons_invalid_tags(self, client: TestClient, db: Session, teacher_token: str):
        """Test mini-lessons API with invalid tags parameter"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="Invalid Tags Class",
            teacher_id=teacher.id,
            invite_code="INVALID"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Call mini-lessons API with empty tags
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should return 422 error
        assert response.status_code == 422

    def test_mini_lessons_max_lessons_per_tag(self, client: TestClient, db: Session, teacher_token: str):
        """Test that at most 3 lessons are returned per tag"""
        # Create test data
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Create class
        test_class = Class(
            name="Max Lessons Test Class",
            teacher_id=teacher.id,
            invite_code="MAXLESSONS"
        )
        db.add(test_class)
        db.commit()
        db.refresh(test_class)

        # Create more than 3 lessons with the same tag
        lessons = []
        for i in range(5):
            lesson = Lesson(
                class_id=test_class.id,
                title=f"Photosynthesis Lesson {i+1}",
                content=f"This is photosynthesis lesson {i+1}...",
                skill_tags=["photosynthesis"]
            )
            lessons.append(lesson)
        
        db.add_all(lessons)
        db.commit()

        # Call mini-lessons API
        response = client.get(
            f"/api/suggestions/mini-lessons?class_id={test_class.id}&tags=photosynthesis",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert len(suggestions) == 1
        assert suggestions[0]["tag"] == "photosynthesis"
        
        # Check that at most 3 lessons are returned
        lessons = suggestions[0]["lessons"]
        assert len(lessons) <= 3
        
        # Check total matches
        assert suggestions[0]["total_matches"] == 5
        assert suggestions[0]["exact_matches"] == 5

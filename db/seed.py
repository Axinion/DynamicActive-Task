#!/usr/bin/env python3
"""
Database seeding script for K12 LMS.
Run this script from the backend directory with the virtual environment activated.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import SessionLocal, create_tables
from app.db.models import User, Class, Enrollment, Lesson, Assignment, Question, Submission, Response
from app.core.security import get_password_hash

def seed_database():
    """Seed the database with demo data."""
    
    # Create tables
    print("Creating database tables...")
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data (in development)
        print("Clearing existing data...")
        db.query(Response).delete()
        db.query(Submission).delete()
        db.query(Question).delete()
        db.query(Assignment).delete()
        db.query(Lesson).delete()
        db.query(Enrollment).delete()
        db.query(Class).delete()
        db.query(User).delete()
        db.commit()
        
        # Create demo users
        print("Creating demo users...")
        
        # Teacher
        teacher = User(
            email="teacher@example.com",
            name="Demo Teacher",
            role="teacher",
            password_hash=get_password_hash("pass")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        # Students
        student1 = User(
            email="student@example.com",
            name="Demo Student",
            role="student",
            password_hash=get_password_hash("pass")
        )
        db.add(student1)
        db.commit()
        db.refresh(student1)
        
        student2 = User(
            email="student2@example.com",
            name="Alex Johnson",
            role="student",
            password_hash=get_password_hash("pass")
        )
        db.add(student2)
        db.commit()
        db.refresh(student2)
        
        student3 = User(
            email="student3@example.com",
            name="Sarah Chen",
            role="student",
            password_hash=get_password_hash("pass")
        )
        db.add(student3)
        db.commit()
        db.refresh(student3)
        
        # Create demo class
        print("Creating demo class...")
        demo_class = Class(
            name="Biology 101",
            teacher_id=teacher.id,
            invite_code="BIO123"
        )
        db.add(demo_class)
        db.commit()
        db.refresh(demo_class)
        
        # Create enrollments for all students
        print("Creating student enrollments...")
        enrollment1 = Enrollment(
            class_id=demo_class.id,
            user_id=student1.id
        )
        db.add(enrollment1)
        
        enrollment2 = Enrollment(
            class_id=demo_class.id,
            user_id=student2.id
        )
        db.add(enrollment2)
        
        enrollment3 = Enrollment(
            class_id=demo_class.id,
            user_id=student3.id
        )
        db.add(enrollment3)
        
        db.commit()
        
        # Create demo lessons
        print("Creating demo lessons...")
        
        # Core photosynthesis lessons
        lesson1 = Lesson(
            class_id=demo_class.id,
            title="Introduction to Photosynthesis",
            content="Photosynthesis is the fundamental process by which plants convert sunlight into energy. In this lesson, we'll explore the basic concepts of how plants use chlorophyll to capture light energy and transform it into chemical energy.",
            skill_tags=["photosynthesis", "chlorophyll", "sunlight", "plant_biology"]
        )
        db.add(lesson1)
        
        lesson2 = Lesson(
            class_id=demo_class.id,
            title="Photosynthesis and Plant Biology",
            content="Photosynthesis is the process by which plants convert sunlight into energy. Plants use chlorophyll to capture light energy and combine it with carbon dioxide and water to produce glucose and oxygen. This process is essential for life on Earth.",
            skill_tags=["chlorophyll", "sunlight", "carbon_dioxide", "oxygen", "photosynthesis", "plant_biology"]
        )
        db.add(lesson2)
        
        lesson3 = Lesson(
            class_id=demo_class.id,
            title="Understanding Chlorophyll and Light Absorption",
            content="Chlorophyll is the green pigment found in plant leaves that is responsible for capturing sunlight energy. This lesson explores how chlorophyll works, why plants are green, and how different wavelengths of light are absorbed and used in photosynthesis.",
            skill_tags=["chlorophyll", "sunlight", "light_absorption", "pigments", "photosynthesis"]
        )
        db.add(lesson3)
        
        lesson4 = Lesson(
            class_id=demo_class.id,
            title="Carbon Dioxide and Oxygen in Photosynthesis",
            content="Learn about the role of carbon dioxide and oxygen in the photosynthesis process. Plants take in carbon dioxide from the atmosphere and release oxygen as a byproduct, making them essential for maintaining atmospheric balance.",
            skill_tags=["carbon_dioxide", "oxygen", "photosynthesis", "atmosphere", "gas_exchange"]
        )
        db.add(lesson4)
        
        lesson5 = Lesson(
            class_id=demo_class.id,
            title="Ecosystem Energy Flow",
            content="Energy flows through ecosystems in a one-way direction, starting with producers that capture sunlight through photosynthesis. Primary consumers eat producers, secondary consumers eat primary consumers, and decomposers break down organic matter, releasing nutrients back into the environment.",
            skill_tags=["ecosystem", "energy_flow", "food_chain", "producers", "consumers"]
        )
        db.add(lesson5)
        
        lesson6 = Lesson(
            class_id=demo_class.id,
            title="Plant Cell Structure and Function",
            content="Explore the structure of plant cells and how they support photosynthesis. Learn about chloroplasts, cell walls, and other organelles that enable plants to capture and convert sunlight energy efficiently.",
            skill_tags=["plant_biology", "cell_structure", "chloroplasts", "organelles"]
        )
        db.add(lesson6)
        
        db.commit()
        
        # Create demo assignment
        print("Creating demo assignment...")
        assignment = Assignment(
            class_id=demo_class.id,
            title="Photosynthesis and Plant Biology Quiz",
            type="quiz",
            rubric={
                "accuracy": 50,
                "method": 30,
                "explanation": 20,
                "keywords": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen"]
            },
            due_at=datetime.now() + timedelta(days=7)
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        # Create demo questions
        print("Creating demo questions...")
        
        # Q1: MCQ question
        question1 = Question(
            assignment_id=assignment.id,
            type="mcq",
            prompt="What is the primary pigment responsible for capturing light energy in plants?",
            options=["Chloroplast", "Chlorophyll", "Carotene", "Xanthophyll"],
            answer_key="Chlorophyll",
            skill_tags=["chlorophyll", "photosynthesis", "plant_biology"]
        )
        db.add(question1)
        
        # Q2: Short answer question with clear model answer and rubric keywords
        question2 = Question(
            assignment_id=assignment.id,
            type="short",
            prompt="Explain the process of photosynthesis. Include the key components and what happens to sunlight, carbon dioxide, and water during this process.",
            answer_key="Photosynthesis is the process by which plants use chlorophyll to capture sunlight energy and combine it with carbon dioxide and water to produce glucose and oxygen. The chlorophyll absorbs sunlight, which provides the energy needed to convert carbon dioxide and water into glucose (food for the plant) and oxygen (released into the atmosphere).",
            skill_tags=["chlorophyll", "sunlight", "carbon_dioxide", "oxygen", "photosynthesis", "plant_biology"]
        )
        db.add(question2)
        
        db.commit()
        
        # Create synthetic student submissions for Phase 3 demos
        print("Creating synthetic student submissions...")
        
        # Student 1: Good submission (high scores)
        submission1 = Submission(
            assignment_id=assignment.id,
            student_id=student1.id,
            ai_score=95.0,
            ai_explanation="Excellent understanding of photosynthesis concepts. Student correctly identified chlorophyll and provided comprehensive explanation of the process."
        )
        db.add(submission1)
        db.commit()
        db.refresh(submission1)
        
        # Student 1 responses
        response1_q1 = Response(
            submission_id=submission1.id,
            question_id=question1.id,
            student_answer="Chlorophyll",
            ai_score=100.0,
            ai_feedback="Perfect! Chlorophyll is indeed the primary pigment responsible for capturing light energy in plants."
        )
        db.add(response1_q1)
        
        response1_q2 = Response(
            submission_id=submission1.id,
            question_id=question2.id,
            student_answer="Photosynthesis is the process where plants use chlorophyll to capture sunlight energy. They combine this sunlight with carbon dioxide and water to produce glucose and oxygen. The chlorophyll absorbs the sunlight, which provides energy to convert carbon dioxide and water into glucose for food and oxygen that gets released into the atmosphere.",
            ai_score=90.0,
            ai_feedback="Excellent answer! You correctly identified all key components: chlorophyll, sunlight, carbon dioxide, water, glucose, and oxygen. Your explanation clearly describes the energy conversion process.",
            matched_keywords=["chlorophyll", "sunlight", "carbon dioxide", "oxygen"]
        )
        db.add(response1_q2)
        
        # Student 2: Mediocre submission (medium scores)
        submission2 = Submission(
            assignment_id=assignment.id,
            student_id=student2.id,
            ai_score=65.0,
            ai_explanation="Partial understanding of photosynthesis. Student got the MCQ correct but struggled with the detailed explanation of the process."
        )
        db.add(submission2)
        db.commit()
        db.refresh(submission2)
        
        # Student 2 responses
        response2_q1 = Response(
            submission_id=submission2.id,
            question_id=question1.id,
            student_answer="Chlorophyll",
            ai_score=100.0,
            ai_feedback="Correct! Chlorophyll is the right answer."
        )
        db.add(response2_q1)
        
        response2_q2 = Response(
            submission_id=submission2.id,
            question_id=question2.id,
            student_answer="Plants make food using sunlight. They take in carbon dioxide and water and turn it into glucose. They also make oxygen. The green stuff in leaves helps with this process.",
            ai_score=30.0,
            ai_feedback="You have the basic idea right - plants do use sunlight to make food and produce oxygen. However, you're missing some key details. Try to mention chlorophyll specifically and explain how sunlight energy is captured and converted.",
            matched_keywords=["sunlight", "carbon dioxide", "oxygen"]
        )
        db.add(response2_q2)
        
        # Student 3: Poor submission (low scores) - for misconception insights
        submission3 = Submission(
            assignment_id=assignment.id,
            student_id=student3.id,
            ai_score=25.0,
            ai_explanation="Limited understanding of photosynthesis concepts. Student struggled with both the MCQ and the detailed explanation, showing several misconceptions."
        )
        db.add(submission3)
        db.commit()
        db.refresh(submission3)
        
        # Student 3 responses
        response3_q1 = Response(
            submission_id=submission3.id,
            question_id=question1.id,
            student_answer="Chloroplast",
            ai_score=0.0,
            ai_feedback="Not quite right. Chloroplast is the organelle that contains chlorophyll, but chlorophyll is the actual pigment that captures light energy."
        )
        db.add(response3_q1)
        
        response3_q2 = Response(
            submission_id=submission3.id,
            question_id=question2.id,
            student_answer="Plants eat sunlight and breathe in oxygen to make food. They use their roots to get water and then make sugar. The leaves are green because they have chloroplasts that help them make food.",
            ai_score=20.0,
            ai_feedback="There are several misconceptions in your answer. Plants don't 'eat' sunlight - they capture its energy. They take in carbon dioxide (not oxygen) and release oxygen. Also, while chloroplasts are involved, the specific pigment is chlorophyll. Try to focus on the energy conversion process.",
            matched_keywords=["sunlight"]
        )
        db.add(response3_q2)
        
        # Create additional assignments for more diverse analytics data
        print("Creating additional assignments for analytics...")
        
        # Assignment 2: Focus on chlorophyll and light absorption
        assignment2 = Assignment(
            class_id=demo_class.id,
            title="Chlorophyll and Light Absorption Quiz",
            type="quiz",
            rubric={
                "keywords": ["chlorophyll", "sunlight", "light_absorption", "pigments"]
            }
        )
        db.add(assignment2)
        db.commit()
        db.refresh(assignment2)
        
        # Assignment 2 questions
        question2_1 = Question(
            assignment_id=assignment2.id,
            type="mcq",
            prompt="What color of light does chlorophyll absorb most effectively?",
            options=["Red", "Blue", "Green", "Yellow"],
            answer_key="Red",
            skill_tags=["chlorophyll", "light_absorption", "pigments"]
        )
        db.add(question2_1)
        
        question2_2 = Question(
            assignment_id=assignment2.id,
            type="short",
            prompt="Explain why plants appear green and how chlorophyll absorbs light energy.",
            answer_key="Plants appear green because chlorophyll reflects green light while absorbing red and blue light. Chlorophyll molecules capture photons from sunlight and convert this light energy into chemical energy through the process of photosynthesis.",
            skill_tags=["chlorophyll", "sunlight", "light_absorption", "pigments"]
        )
        db.add(question2_2)
        
        # Assignment 3: Focus on carbon dioxide and oxygen
        assignment3 = Assignment(
            class_id=demo_class.id,
            title="Gas Exchange in Photosynthesis",
            type="quiz",
            rubric={
                "keywords": ["carbon_dioxide", "oxygen", "gas_exchange", "atmosphere"]
            }
        )
        db.add(assignment3)
        db.commit()
        db.refresh(assignment3)
        
        # Assignment 3 questions
        question3_1 = Question(
            assignment_id=assignment3.id,
            type="mcq",
            prompt="What gas do plants take in during photosynthesis?",
            options=["Oxygen", "Carbon Dioxide", "Nitrogen", "Water Vapor"],
            answer_key="Carbon Dioxide",
            skill_tags=["carbon_dioxide", "photosynthesis", "gas_exchange"]
        )
        db.add(question3_1)
        
        question3_2 = Question(
            assignment_id=assignment3.id,
            type="short",
            prompt="Describe the gas exchange that occurs during photosynthesis. What gases are taken in and what is released?",
            answer_key="During photosynthesis, plants take in carbon dioxide from the atmosphere through their leaves and release oxygen as a byproduct. This gas exchange is essential for maintaining atmospheric balance and provides oxygen for other living organisms.",
            skill_tags=["carbon_dioxide", "oxygen", "gas_exchange", "atmosphere"]
        )
        db.add(question3_2)
        
        db.commit()
        
        # Create additional submissions for better clustering
        print("Creating additional submissions for analytics clustering...")
        
        # Student 1: Additional submissions (good performance)
        submission1_2 = Submission(
            assignment_id=assignment2.id,
            student_id=student1.id,
            ai_score=88.0,
            ai_explanation="Good understanding of chlorophyll and light absorption concepts."
        )
        db.add(submission1_2)
        db.commit()
        db.refresh(submission1_2)
        
        response1_2_q1 = Response(
            submission_id=submission1_2.id,
            question_id=question2_1.id,
            student_answer="Red",
            ai_score=100.0,
            ai_feedback="Correct! Chlorophyll absorbs red light most effectively."
        )
        db.add(response1_2_q1)
        
        response1_2_q2 = Response(
            submission_id=submission1_2.id,
            question_id=question2_2.id,
            student_answer="Plants appear green because chlorophyll reflects green light while absorbing red and blue light. The chlorophyll molecules capture photons and convert light energy into chemical energy.",
            ai_score=85.0,
            ai_feedback="Excellent explanation! You correctly described the light absorption and energy conversion process.",
            matched_keywords=["chlorophyll", "sunlight", "light_absorption"]
        )
        db.add(response1_2_q2)
        
        # Student 2: Additional submissions (mixed performance)
        submission2_2 = Submission(
            assignment_id=assignment2.id,
            student_id=student2.id,
            ai_score=45.0,
            ai_explanation="Some understanding of chlorophyll but confused about light absorption."
        )
        db.add(submission2_2)
        db.commit()
        db.refresh(submission2_2)
        
        response2_2_q1 = Response(
            submission_id=submission2_2.id,
            question_id=question2_1.id,
            student_answer="Green",
            ai_score=0.0,
            ai_feedback="Not quite right. Chlorophyll reflects green light, so it doesn't absorb it effectively."
        )
        db.add(response2_2_q1)
        
        response2_2_q2 = Response(
            submission_id=submission2_2.id,
            question_id=question2_2.id,
            student_answer="Plants are green because they have chlorophyll. Chlorophyll helps plants get energy from the sun.",
            ai_score=30.0,
            ai_feedback="You're on the right track with chlorophyll and sunlight, but try to be more specific about which colors of light are absorbed and how the energy conversion works.",
            matched_keywords=["chlorophyll", "sunlight"]
        )
        db.add(response2_2_q2)
        
        # Student 3: Additional submissions (poor performance - for clustering)
        submission3_2 = Submission(
            assignment_id=assignment2.id,
            student_id=student3.id,
            ai_score=15.0,
            ai_explanation="Significant misconceptions about chlorophyll and light absorption."
        )
        db.add(submission3_2)
        db.commit()
        db.refresh(submission3_2)
        
        response3_2_q1 = Response(
            submission_id=submission3_2.id,
            question_id=question2_1.id,
            student_answer="Green",
            ai_score=0.0,
            ai_feedback="Incorrect. Chlorophyll reflects green light, so it doesn't absorb it effectively."
        )
        db.add(response3_2_q1)
        
        response3_2_q2 = Response(
            submission_id=submission3_2.id,
            question_id=question2_2.id,
            student_answer="Plants are green because they eat green food. Chlorophyll is like a solar panel that catches sunlight to make energy.",
            ai_score=10.0,
            ai_feedback="There are several misconceptions here. Plants don't 'eat' green food, and while the solar panel analogy is creative, try to focus on the specific light absorption properties of chlorophyll.",
            matched_keywords=["sunlight"]
        )
        db.add(response3_2_q2)
        
        # Additional submissions for assignment 3 (carbon dioxide/oxygen focus)
        submission1_3 = Submission(
            assignment_id=assignment3.id,
            student_id=student1.id,
            ai_score=92.0,
            ai_explanation="Excellent understanding of gas exchange in photosynthesis."
        )
        db.add(submission1_3)
        db.commit()
        db.refresh(submission1_3)
        
        response1_3_q1 = Response(
            submission_id=submission1_3.id,
            question_id=question3_1.id,
            student_answer="Carbon Dioxide",
            ai_score=100.0,
            ai_feedback="Perfect! Plants take in carbon dioxide during photosynthesis."
        )
        db.add(response1_3_q1)
        
        response1_3_q2 = Response(
            submission_id=submission1_3.id,
            question_id=question3_2.id,
            student_answer="During photosynthesis, plants take in carbon dioxide from the atmosphere and release oxygen as a byproduct. This gas exchange helps maintain atmospheric balance and provides oxygen for other organisms.",
            ai_score=90.0,
            ai_feedback="Excellent answer! You clearly explained the gas exchange process and its importance.",
            matched_keywords=["carbon_dioxide", "oxygen", "atmosphere"]
        )
        db.add(response1_3_q2)
        
        # Student 2: Assignment 3 (confused about gas exchange)
        submission2_3 = Submission(
            assignment_id=assignment3.id,
            student_id=student2.id,
            ai_score=40.0,
            ai_explanation="Confused about the direction of gas exchange in photosynthesis."
        )
        db.add(submission2_3)
        db.commit()
        db.refresh(submission2_3)
        
        response2_3_q1 = Response(
            submission_id=submission2_3.id,
            question_id=question3_1.id,
            student_answer="Oxygen",
            ai_score=0.0,
            ai_feedback="Not quite right. Plants take in carbon dioxide, not oxygen, during photosynthesis."
        )
        db.add(response2_3_q1)
        
        response2_3_q2 = Response(
            submission_id=submission2_3.id,
            question_id=question3_2.id,
            student_answer="Plants breathe in oxygen and breathe out carbon dioxide, just like animals do. They use the oxygen to make food and release carbon dioxide as waste.",
            ai_score=20.0,
            ai_feedback="This is a common misconception! Plants actually do the opposite - they take in carbon dioxide and release oxygen during photosynthesis. The process is different from animal respiration.",
            matched_keywords=["oxygen", "carbon_dioxide"]
        )
        db.add(response2_3_q2)
        
        # Student 3: Assignment 3 (major misconceptions)
        submission3_3 = Submission(
            assignment_id=assignment3.id,
            student_id=student3.id,
            ai_score=10.0,
            ai_explanation="Major misconceptions about gas exchange and photosynthesis process."
        )
        db.add(submission3_3)
        db.commit()
        db.refresh(submission3_3)
        
        response3_3_q1 = Response(
            submission_id=submission3_3.id,
            question_id=question3_1.id,
            student_answer="Oxygen",
            ai_score=0.0,
            ai_feedback="Incorrect. Plants take in carbon dioxide during photosynthesis, not oxygen."
        )
        db.add(response3_3_q1)
        
        response3_3_q2 = Response(
            submission_id=submission3_3.id,
            question_id=question3_2.id,
            student_answer="Plants breathe oxygen like we do and make carbon dioxide. They use the oxygen to help them grow and make food from sunlight.",
            ai_score=5.0,
            ai_feedback="This shows a fundamental misunderstanding of photosynthesis. Plants actually take in carbon dioxide and release oxygen, which is the opposite of what you described. The oxygen they release is a byproduct of making food from sunlight.",
            matched_keywords=["oxygen"]
        )
        db.add(response3_3_q2)
        
        db.commit()
        
        # Create second class for more diverse demo data
        print("Creating second demo class...")
        math_class = Class(
            name="Mathematics 201",
            teacher_id=teacher.id,
            invite_code="MATH456"
        )
        db.add(math_class)
        db.commit()
        db.refresh(math_class)
        
        # Enroll students in math class
        math_enrollment1 = Enrollment(
            class_id=math_class.id,
            user_id=student1.id
        )
        db.add(math_enrollment1)
        
        math_enrollment2 = Enrollment(
            class_id=math_class.id,
            user_id=student2.id
        )
        db.add(math_enrollment2)
        
        db.commit()
        
        # Create math lessons
        print("Creating math lessons...")
        math_lesson1 = Lesson(
            class_id=math_class.id,
            title="Introduction to Fractions",
            content="Fractions represent parts of a whole. A fraction consists of a numerator (top number) and a denominator (bottom number). The denominator tells us how many equal parts the whole is divided into, and the numerator tells us how many of those parts we have.",
            skill_tags=["fractions", "numerator", "denominator", "basic_math"]
        )
        db.add(math_lesson1)
        
        math_lesson2 = Lesson(
            class_id=math_class.id,
            title="Adding and Subtracting Fractions",
            content="To add or subtract fractions, they must have the same denominator. If they don't, we need to find a common denominator first. Once the denominators are the same, we add or subtract the numerators and keep the denominator the same.",
            skill_tags=["fractions", "addition", "subtraction", "common_denominator"]
        )
        db.add(math_lesson2)
        
        math_lesson3 = Lesson(
            class_id=math_class.id,
            title="Understanding Decimals",
            content="Decimals are another way to represent fractions. The decimal point separates the whole number part from the fractional part. Each place to the right of the decimal point represents a fraction with a denominator that is a power of 10.",
            skill_tags=["decimals", "decimal_point", "place_value", "fractions"]
        )
        db.add(math_lesson3)
        
        db.commit()
        
        # Create math assignment
        print("Creating math assignment...")
        math_assignment = Assignment(
            class_id=math_class.id,
            title="Fractions and Decimals Quiz",
            type="quiz",
            rubric={
                "keywords": ["fractions", "decimals", "numerator", "denominator", "addition", "subtraction"]
            }
        )
        db.add(math_assignment)
        db.commit()
        db.refresh(math_assignment)
        
        # Create math questions
        math_question1 = Question(
            assignment_id=math_assignment.id,
            type="mcq",
            prompt="What is 1/2 + 1/4?",
            options=["1/6", "2/6", "3/4", "1/4"],
            answer_key="3/4",
            skill_tags=["fractions", "addition"]
        )
        db.add(math_question1)
        
        math_question2 = Question(
            assignment_id=math_assignment.id,
            type="short",
            prompt="Explain how to add fractions with different denominators. Use 1/3 + 1/6 as an example.",
            answer_key="To add fractions with different denominators, find a common denominator. For 1/3 + 1/6, the common denominator is 6. Convert 1/3 to 2/6, then add: 2/6 + 1/6 = 3/6 = 1/2.",
            skill_tags=["fractions", "addition", "common_denominator"]
        )
        db.add(math_question2)
        
        math_question3 = Question(
            assignment_id=math_assignment.id,
            type="short",
            prompt="Convert 0.75 to a fraction in its simplest form.",
            answer_key="0.75 = 75/100 = 3/4",
            skill_tags=["decimals", "fractions", "conversion"]
        )
        db.add(math_question3)
        
        db.commit()
        db.refresh(math_question1)
        db.refresh(math_question2)
        db.refresh(math_question3)
        
        # Create math submissions with low scores for insights
        print("Creating math submissions...")
        
        # Student 1: Good performance
        math_submission1 = Submission(
            assignment_id=math_assignment.id,
            student_id=student1.id,
            submitted_at=datetime.now(timezone.utc) - timedelta(days=1),
            ai_score=85.0,
            ai_explanation="Good understanding of fractions and decimals with minor calculation errors."
        )
        db.add(math_submission1)
        db.commit()
        db.refresh(math_submission1)
        
        # Student 1 responses
        math_response1_q1 = Response(
            submission_id=math_submission1.id,
            question_id=math_question1.id,
            student_answer="3/4",
            ai_score=100.0,
            ai_feedback="Correct! 1/2 + 1/4 = 2/4 + 1/4 = 3/4."
        )
        db.add(math_response1_q1)
        
        math_response1_q2 = Response(
            submission_id=math_submission1.id,
            question_id=math_question2.id,
            student_answer="To add fractions with different denominators, find a common denominator. For 1/3 + 1/6, the common denominator is 6. Convert 1/3 to 2/6, then add: 2/6 + 1/6 = 3/6 = 1/2.",
            ai_score=90.0,
            ai_feedback="Excellent explanation! You correctly identified the common denominator and showed the conversion process.",
            matched_keywords=["fractions", "addition", "common_denominator"]
        )
        db.add(math_response1_q2)
        
        math_response1_q3 = Response(
            submission_id=math_submission1.id,
            question_id=math_question3.id,
            student_answer="0.75 = 75/100 = 3/4",
            ai_score=100.0,
            ai_feedback="Perfect! You correctly converted the decimal to a fraction and simplified it."
        )
        db.add(math_response1_q3)
        
        # Student 2: Poor performance for insights
        math_submission2 = Submission(
            assignment_id=math_assignment.id,
            student_id=student2.id,
            submitted_at=datetime.now(timezone.utc) - timedelta(days=2),
            ai_score=25.0,
            ai_explanation="Significant misconceptions about fractions and decimals. Student struggles with basic concepts."
        )
        db.add(math_submission2)
        db.commit()
        db.refresh(math_submission2)
        
        # Student 2 responses with misconceptions
        math_response2_q1 = Response(
            submission_id=math_submission2.id,
            question_id=math_question1.id,
            student_answer="2/6",
            ai_score=0.0,
            ai_feedback="Incorrect. You added the numerators and denominators separately. To add fractions, you need a common denominator first."
        )
        db.add(math_response2_q1)
        
        math_response2_q2 = Response(
            submission_id=math_submission2.id,
            question_id=math_question2.id,
            student_answer="You just add the top numbers and bottom numbers. So 1/3 + 1/6 = 2/9 because 1+1=2 and 3+6=9.",
            ai_score=10.0,
            ai_feedback="This shows a common misconception. You cannot add fractions by adding numerators and denominators separately. You need to find a common denominator first.",
            matched_keywords=["fractions"]
        )
        db.add(math_response2_q2)
        
        math_response2_q3 = Response(
            submission_id=math_submission2.id,
            question_id=math_question3.id,
            student_answer="0.75 = 75/1",
            ai_score=15.0,
            ai_feedback="Incorrect. The decimal 0.75 represents 75 hundredths, not 75 wholes. It should be 75/100, which simplifies to 3/4."
        )
        db.add(math_response2_q3)
        
        db.commit()
        
        print("✅ Enhanced Phase 3 Seed complete!")
        print(f"Created:")
        print(f"  - 1 teacher: {teacher.email}")
        print(f"  - 3 students: {student1.email}, {student2.email}, {student3.email}")
        print(f"  - 2 classes:")
        print(f"    * {demo_class.name} (invite code: {demo_class.invite_code})")
        print(f"    * {math_class.name} (invite code: {math_class.invite_code})")
        print(f"  - 9 lessons covering multiple skill tags")
        print(f"  - 4 assignments with 9 total questions")
        print(f"  - 11 synthetic submissions with diverse performance levels")
        print(f"\nDemo credentials:")
        print(f"  Teacher: teacher@example.com / pass")
        print(f"  Students: student@example.com / pass, student2@example.com / pass, student3@example.com / pass")
        print(f"\n📋 Quick Navigation:")
        print(f"  Class Invite Codes:")
        print(f"    - Biology 101: {demo_class.invite_code}")
        print(f"    - Mathematics 201: {math_class.invite_code}")
        print(f"  Assignment IDs for quick testing:")
        print(f"    - Biology Assignment 1: {assignment.id}")
        print(f"    - Math Assignment: {math_assignment.id}")
        print(f"\n🎯 Enhanced Analytics Features:")
        print(f"  📚 Two Classes with Diverse Content:")
        print(f"     - Biology 101: Photosynthesis, chlorophyll, plant biology")
        print(f"     - Mathematics 201: Fractions, decimals, basic arithmetic")
        print(f"  📝 4 Assignments with diverse skill focus:")
        print(f"     - Biology Assignment 1: General photosynthesis (chlorophyll, sunlight, carbon dioxide, oxygen)")
        print(f"     - Biology Assignment 2: Chlorophyll and light absorption (pigments, light_absorption)")
        print(f"     - Biology Assignment 3: Gas exchange (carbon_dioxide, oxygen, atmosphere)")
        print(f"     - Math Assignment: Fractions and decimals (fractions, addition, common_denominator)")
        print(f"  🤖 AI Grading: Short answers auto-graded with keyword matching and semantic similarity")
        print(f"  📊 Student Performance Across Multiple Skill Tags:")
        print(f"     - Student 1: High scores (85-95%) - Strong understanding across all topics")
        print(f"     - Student 2: Medium scores (30-65%) - Partial understanding with specific gaps")
        print(f"     - Student 3: Low scores (5-25%) - Multiple misconceptions for clustering analysis")
        print(f"\n🧪 Analytics Test Flows:")
        print(f"  🔬 Misconception Clustering:")
        print(f"     1. Login as teacher → View insights → See clustered misconceptions by skill tag")
        print(f"     2. Test weekly/monthly time-based analysis")
        print(f"     3. Analyze common errors across different skill areas")
        print(f"  🎯 Mini-Lesson Suggestions:")
        print(f"     1. Login as teacher → Get suggestions for specific skill tags")
        print(f"     2. Test rule-based ranking (tag match + recency)")
        print(f"     3. Get suggestions for student weak skills automatically")
        print(f"  📈 Student Progress Tracking:")
        print(f"     1. Login as teacher → View student progress by skill mastery")
        print(f"     2. Test skill mastery calculation across multiple assignments")
        print(f"     3. Identify weak skills for targeted remediation")
        print(f"  ✏️ Teacher Overrides:")
        print(f"     1. Login as teacher → Override individual response scores")
        print(f"     2. Test audit trail preservation (AI scores remain unchanged)")
        print(f"\n🌟 Enhanced Analytics Features:")
        print(f"  - Time-based misconception clustering (weekly/monthly)")
        print(f"  - Rule-based mini-lesson suggestions with tag matching")
        print(f"  - Comprehensive skill mastery tracking across multiple assignments")
        print(f"  - Diverse student performance data for robust clustering")
        print(f"  - Database indexes for optimal analytics performance")
        print(f"  - Multiple skill tags for targeted remediation suggestions")
        print(f"\n🎉 Seed complete. Teacher creds: teacher@example.com / pass")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

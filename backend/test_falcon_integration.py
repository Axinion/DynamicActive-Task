#!/usr/bin/env python3
"""
Test script for Falcon-H1-1B-Base model integration.
Run this script to verify the Falcon model is working correctly.
"""

import sys
import os

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.falcon_service import (
    generate_feedback,
    generate_learning_tips,
    analyze_misconception_pattern,
    get_model_info
)

def test_falcon_integration():
    """Test the Falcon model integration."""
    print("🚀 Testing Falcon-H1-1B-Base Integration")
    print("=" * 50)
    
    # Test 1: Model Info
    print("\n1. Testing Model Info...")
    try:
        model_info = get_model_info()
        print(f"✅ Model Info: {model_info}")
    except Exception as e:
        print(f"❌ Model Info Failed: {e}")
        return False
    
    # Test 2: Feedback Generation
    print("\n2. Testing Feedback Generation...")
    try:
        student_answer = "Plants need sunlight to grow and make food through photosynthesis."
        model_answer = "Plants use sunlight, water, and carbon dioxide to produce glucose through photosynthesis, which occurs in the chloroplasts."
        question_prompt = "Explain how plants make their own food."
        rubric_keywords = ["photosynthesis", "sunlight", "glucose", "chloroplasts"]
        score = 0.7
        
        feedback = generate_feedback(
            student_answer=student_answer,
            model_answer=model_answer,
            question_prompt=question_prompt,
            rubric_keywords=rubric_keywords,
            score=score
        )
        print(f"✅ Generated Feedback: {feedback[:100]}...")
    except Exception as e:
        print(f"❌ Feedback Generation Failed: {e}")
        return False
    
    # Test 3: Learning Tips
    print("\n3. Testing Learning Tips Generation...")
    try:
        tips = generate_learning_tips(
            student_answer=student_answer,
            model_answer=model_answer,
            skill_tags=["biology", "photosynthesis"]
        )
        print(f"✅ Generated Learning Tips: {tips}")
    except Exception as e:
        print(f"❌ Learning Tips Generation Failed: {e}")
        return False
    
    # Test 4: Misconception Analysis
    print("\n4. Testing Misconception Analysis...")
    try:
        responses = [
            "Plants eat sunlight to grow",
            "Sunlight is food for plants",
            "Plants don't need water to make food"
        ]
        question_prompts = [
            "How do plants make food?",
            "What do plants need for photosynthesis?",
            "What is the role of water in plant growth?"
        ]
        skill_tags = ["photosynthesis", "plant biology"]
        
        analysis = analyze_misconception_pattern(
            responses=responses,
            question_prompts=question_prompts,
            skill_tags=skill_tags
        )
        print(f"✅ Misconception Analysis: {analysis}")
    except Exception as e:
        print(f"❌ Misconception Analysis Failed: {e}")
        return False
    
    print("\n🎉 All Falcon integration tests passed!")
    return True

def test_grading_integration():
    """Test the enhanced grading service with Falcon."""
    print("\n🔬 Testing Enhanced Grading Integration")
    print("=" * 50)
    
    try:
        from app.services.grading import score_short_answer
        
        student_answer = "To solve 2x + 3 = 7, I subtract 3 from both sides to isolate the variable x"
        model_answer = "To solve linear equations, isolate the variable by performing inverse operations on both sides"
        rubric_keywords = ["isolate", "variable", "inverse", "operations", "solve"]
        question_prompt = "Explain how to solve the equation 2x + 3 = 7"
        
        result = score_short_answer(
            student_answer=student_answer,
            model_answer=model_answer,
            rubric_keywords=rubric_keywords,
            question_prompt=question_prompt,
            use_falcon_feedback=True
        )
        
        print(f"✅ Enhanced Grading Result:")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Enhanced Feedback: {result.get('enhanced_feedback', 'N/A')[:100]}...")
        print(f"   Learning Tips: {result.get('learning_tips', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Grading Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Falcon-H1-1B-Base Integration Test Suite")
    print("=" * 60)
    
    # Test Falcon integration
    falcon_success = test_falcon_integration()
    
    # Test grading integration
    grading_success = test_grading_integration()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Falcon Integration: {'✅ PASSED' if falcon_success else '❌ FAILED'}")
    print(f"Grading Integration: {'✅ PASSED' if grading_success else '❌ FAILED'}")
    
    if falcon_success and grading_success:
        print("\n🎉 All tests passed! Falcon-H1-1B-Base is ready to use.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)


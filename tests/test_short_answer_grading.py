"""
Test short answer grading API endpoint
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_short_answer_grading_good_answer():
    """Test grading a good short answer that should score above threshold"""
    
    # Test data for a good answer
    good_answer_data = {
        "student_answer": "Plants use chlorophyll to capture sunlight energy and convert carbon dioxide and water into glucose and oxygen through the process of photosynthesis. This process occurs in the chloroplasts and requires sunlight as the energy source.",
        "model_answer": "Plants use chlorophyll to capture light energy from the sun and convert carbon dioxide and water into glucose and oxygen through photosynthesis. This process occurs in chloroplasts and requires sunlight as an energy source.",
        "rubric_keywords": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen", "photosynthesis", "glucose"]
    }
    
    response = client.post("/api/grade/short-answer", json=good_answer_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "score" in data
    assert "confidence" in data
    assert "explanation" in data
    assert "matched_keywords" in data
    
    # Check score is above threshold (0.7)
    assert data["score"] > 0.7
    assert 0 <= data["score"] <= 1
    
    # Check confidence is reasonable
    assert 0 <= data["confidence"] <= 1
    
    # Check explanation is present and meaningful
    assert data["explanation"] is not None
    assert len(data["explanation"]) > 10
    assert isinstance(data["explanation"], str)
    
    # Check matched keywords
    assert isinstance(data["matched_keywords"], list)
    assert len(data["matched_keywords"]) > 0
    # Should match most keywords from rubric
    assert len(data["matched_keywords"]) >= 4  # At least 4 out of 6 keywords


def test_short_answer_grading_weak_answer():
    """Test grading a weak short answer that should score below threshold"""
    
    # Test data for a weak answer
    weak_answer_data = {
        "student_answer": "Plants make food using light. They need water and air.",
        "model_answer": "Plants use chlorophyll to capture light energy from the sun and convert carbon dioxide and water into glucose and oxygen through photosynthesis. This process occurs in chloroplasts and requires sunlight as an energy source.",
        "rubric_keywords": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen", "photosynthesis", "glucose"]
    }
    
    response = client.post("/api/grade/short-answer", json=weak_answer_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "score" in data
    assert "confidence" in data
    assert "explanation" in data
    assert "matched_keywords" in data
    
    # Check score is below threshold (0.7)
    assert data["score"] < 0.7
    assert 0 <= data["score"] <= 1
    
    # Check confidence is reasonable
    assert 0 <= data["confidence"] <= 1
    
    # Check explanation is present and meaningful
    assert data["explanation"] is not None
    assert len(data["explanation"]) > 10
    assert isinstance(data["explanation"], str)
    
    # Check matched keywords (should be fewer)
    assert isinstance(data["matched_keywords"], list)
    assert len(data["matched_keywords"]) < 4  # Fewer keywords matched


def test_short_answer_grading_edge_cases():
    """Test edge cases for short answer grading"""
    
    # Test with empty student answer
    empty_answer_data = {
        "student_answer": "",
        "model_answer": "Plants use chlorophyll for photosynthesis.",
        "rubric_keywords": ["chlorophyll", "photosynthesis"]
    }
    
    response = client.post("/api/grade/short-answer", json=empty_answer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 0.0
    assert len(data["matched_keywords"]) == 0
    
    # Test with very long student answer
    long_answer = "Plants use chlorophyll to capture sunlight energy and convert carbon dioxide and water into glucose and oxygen through the process of photosynthesis. " * 10
    long_answer_data = {
        "student_answer": long_answer,
        "model_answer": "Plants use chlorophyll for photosynthesis.",
        "rubric_keywords": ["chlorophyll", "photosynthesis"]
    }
    
    response = client.post("/api/grade/short-answer", json=long_answer_data)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["score"] <= 1
    
    # Test with no rubric keywords
    no_keywords_data = {
        "student_answer": "Plants use chlorophyll for photosynthesis.",
        "model_answer": "Plants use chlorophyll for photosynthesis.",
        "rubric_keywords": []
    }
    
    response = client.post("/api/grade/short-answer", json=no_keywords_data)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["score"] <= 1
    assert len(data["matched_keywords"]) == 0


def test_short_answer_grading_validation():
    """Test input validation for short answer grading"""
    
    # Test missing required fields
    incomplete_data = {
        "student_answer": "Test answer"
        # Missing model_answer and rubric_keywords
    }
    
    response = client.post("/api/grade/short-answer", json=incomplete_data)
    assert response.status_code == 422  # Validation error
    
    # Test invalid data types
    invalid_data = {
        "student_answer": 123,  # Should be string
        "model_answer": "Test model",
        "rubric_keywords": "not a list"  # Should be list
    }
    
    response = client.post("/api/grade/short-answer", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_short_answer_grading_performance():
    """Test performance with various answer lengths and complexities"""
    
    # Test with complex scientific answer
    complex_answer_data = {
        "student_answer": "Photosynthesis is a complex biochemical process where plants, algae, and certain bacteria convert light energy into chemical energy. The process occurs in two main stages: the light-dependent reactions in the thylakoid membranes of chloroplasts, where chlorophyll and other pigments absorb photons and generate ATP and NADPH, and the light-independent reactions (Calvin cycle) in the stroma, where carbon dioxide is fixed and reduced to produce glucose. The overall equation is 6CO2 + 6H2O + light energy → C6H12O6 + 6O2.",
        "model_answer": "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in chloroplasts and involves chlorophyll capturing light to produce glucose and oxygen from carbon dioxide and water.",
        "rubric_keywords": ["photosynthesis", "chlorophyll", "glucose", "oxygen", "carbon dioxide", "light energy", "chloroplasts"]
    }
    
    response = client.post("/api/grade/short-answer", json=complex_answer_data)
    assert response.status_code == 200
    data = response.json()
    
    # Should score well due to comprehensive coverage
    assert data["score"] > 0.6
    assert len(data["matched_keywords"]) >= 5
    
    # Test with simple but correct answer
    simple_answer_data = {
        "student_answer": "Plants make food using sunlight.",
        "model_answer": "Plants use sunlight to make food through photosynthesis.",
        "rubric_keywords": ["plants", "sunlight", "food", "photosynthesis"]
    }
    
    response = client.post("/api/grade/short-answer", json=simple_answer_data)
    assert response.status_code == 200
    data = response.json()
    
    # Should score moderately due to keyword matching
    assert 0.3 <= data["score"] <= 0.8


def test_short_answer_grading_consistency():
    """Test consistency of grading for similar answers"""
    
    base_data = {
        "model_answer": "Plants use chlorophyll to capture light energy and convert carbon dioxide and water into glucose and oxygen through photosynthesis.",
        "rubric_keywords": ["chlorophyll", "light energy", "carbon dioxide", "water", "glucose", "oxygen", "photosynthesis"]
    }
    
    # Test similar answers should get similar scores
    similar_answers = [
        "Plants use chlorophyll to capture light energy and convert carbon dioxide and water into glucose and oxygen through photosynthesis.",
        "Plants utilize chlorophyll to capture light energy and convert carbon dioxide and water into glucose and oxygen through photosynthesis.",
        "Plants employ chlorophyll to capture light energy and convert carbon dioxide and water into glucose and oxygen through photosynthesis."
    ]
    
    scores = []
    for answer in similar_answers:
        test_data = {**base_data, "student_answer": answer}
        response = client.post("/api/grade/short-answer", json=test_data)
        assert response.status_code == 200
        data = response.json()
        scores.append(data["score"])
    
    # Scores should be very similar (within 0.1)
    assert max(scores) - min(scores) < 0.1
    
    # All should score high since they're essentially correct
    assert all(score > 0.8 for score in scores)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

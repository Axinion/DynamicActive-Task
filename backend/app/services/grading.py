"""
Grading service for automated short-answer question scoring.
Provides semantic similarity and keyword coverage analysis with enhanced AI feedback.
"""

import re
from typing import List, Dict, Any
import numpy as np
from .embeddings import embed_text
from .falcon_service import generate_feedback, generate_learning_tips


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score between 0 and 1
        
    Example:
        >>> a = np.array([1, 0, 0])
        >>> b = np.array([0, 1, 0])
        >>> cosine(a, b)  # 0.0 (orthogonal)
        >>> cosine(a, a)  # 1.0 (identical)
    """
    if len(a) == 0 or len(b) == 0:
        return 0.0
    
    # Since embeddings are L2-normalized, cosine similarity is just dot product
    similarity = np.dot(a, b)
    
    # Ensure result is in [0, 1] range
    return max(0.0, min(1.0, similarity))


def keyword_coverage(answer: str, keywords: List[str]) -> float:
    """
    Calculate keyword coverage score for an answer.
    
    Args:
        answer: Student's answer text
        keywords: List of important keywords to look for
        
    Returns:
        Coverage score between 0 and 1 (unique hits / total keywords)
        
    Example:
        >>> answer = "The process involves isolating the variable and solving"
        >>> keywords = ["isolate", "variable", "solve", "equation"]
        >>> keyword_coverage(answer, keywords)  # 0.75 (3 out of 4 keywords found)
    """
    if not answer or not keywords:
        return 0.0
    
    # Convert to lowercase for case-insensitive matching
    answer_lower = answer.lower()
    keywords_lower = [kw.lower() for kw in keywords]
    
    # Find unique keyword matches
    matched_keywords = []
    for keyword in keywords_lower:
        if keyword in answer_lower:
            matched_keywords.append(keyword)
    
    # Return ratio of matched keywords to total keywords
    return len(matched_keywords) / len(keywords_lower)


def score_short_answer(
    student_answer: str, 
    model_answer: str, 
    rubric_keywords: List[str],
    question_prompt: str = "",
    use_falcon_feedback: bool = True
) -> Dict[str, Any]:
    """
    Score a short answer question using semantic similarity and keyword coverage.
    Enhanced with Falcon-H1-1B-Base model for better feedback generation.
    
    Args:
        student_answer: Student's submitted answer
        model_answer: Model/expected answer for comparison
        rubric_keywords: List of important keywords from the rubric
        question_prompt: The original question prompt (optional)
        use_falcon_feedback: Whether to use Falcon model for enhanced feedback
        
    Returns:
        Dictionary containing:
        - score: Final score between 0 and 1
        - confidence: Confidence level between 0 and 1
        - explanation: Human-readable explanation
        - matched_keywords: List of keywords found in student answer
        - enhanced_feedback: AI-generated feedback (if Falcon is used)
        - learning_tips: Personalized learning suggestions (if Falcon is used)
        
    Example:
        >>> student = "To solve 2x + 3 = 7, I isolate x by subtracting 3 from both sides"
        >>> model = "To solve linear equations, isolate the variable by performing inverse operations"
        >>> keywords = ["isolate", "variable", "inverse", "operations"]
        >>> result = score_short_answer(student, model, keywords)
        >>> print(result["score"])  # Score between 0 and 1
        >>> print(result["explanation"])  # Human-readable explanation
    """
    if not student_answer or not student_answer.strip():
        return {
            "score": 0.0,
            "confidence": 0.0,
            "explanation": "No answer provided.",
            "matched_keywords": [],
            "enhanced_feedback": "Please provide an answer to receive feedback.",
            "learning_tips": {
                "praise": "We're here to help you learn!",
                "suggestions": ["Try to answer the question to the best of your ability", "Don't worry about being perfect - just give it your best shot"],
                "study_tip": "Review the material and try again"
            }
        }
    
    # Generate embeddings for semantic similarity
    try:
        student_embedding = embed_text(student_answer)
        model_embedding = embed_text(model_answer)
        sim = cosine(student_embedding, model_embedding)
    except Exception as e:
        # Fallback to keyword-only scoring if embedding fails
        sim = 0.0
        print(f"Warning: Embedding failed, using keyword-only scoring: {e}")
    
    # Calculate keyword coverage
    kw_score = keyword_coverage(student_answer, rubric_keywords)
    
    # Find matched keywords for explanation
    matched_keywords = []
    if rubric_keywords:
        answer_lower = student_answer.lower()
        for keyword in rubric_keywords:
            if keyword.lower() in answer_lower:
                matched_keywords.append(keyword)
    
    # Calculate final score: 70% semantic similarity + 30% keyword coverage
    final_score = 0.7 * sim + 0.3 * kw_score
    final_score = max(0.0, min(1.0, final_score))  # Clip to [0, 1]
    
    # Calculate confidence as average of similarity and keyword coverage
    confidence = (sim + kw_score) / 2
    
    # Generate explanation
    explanation_parts = []
    
    # Add similarity assessment
    if sim >= 0.8:
        sim_level = "high"
    elif sim >= 0.6:
        sim_level = "medium"
    else:
        sim_level = "low"
    
    explanation_parts.append(f"Semantic similarity: {sim_level}")
    
    # Add keyword information
    if matched_keywords:
        if len(matched_keywords) == len(rubric_keywords):
            explanation_parts.append("all key concepts covered")
        else:
            explanation_parts.append(f"key concepts covered: {', '.join(matched_keywords)}")
    else:
        explanation_parts.append("no key concepts identified")
    
    explanation = f"Answer shows {sim_level} similarity to expected response. " + \
                 f"Student {'demonstrates' if matched_keywords else 'lacks'} " + \
                 f"{'understanding of' if matched_keywords else 'understanding of'} " + \
                 f"{', '.join(matched_keywords) if matched_keywords else 'key concepts'}."
    
    # Enhanced feedback using Falcon model
    enhanced_feedback = explanation
    learning_tips = None
    
    if use_falcon_feedback:
        try:
            # Generate enhanced feedback using Falcon model
            enhanced_feedback = generate_feedback(
                student_answer=student_answer,
                model_answer=model_answer,
                question_prompt=question_prompt or "Answer the following question",
                rubric_keywords=rubric_keywords,
                score=final_score
            )
            
            # Generate learning tips
            learning_tips = generate_learning_tips(
                student_answer=student_answer,
                model_answer=model_answer,
                skill_tags=rubric_keywords
            )
            
        except Exception as e:
            print(f"Warning: Falcon feedback generation failed, using fallback: {e}")
            # Keep the original explanation as fallback
            enhanced_feedback = explanation
    
    result = {
        "score": float(final_score),  # Convert to Python float for JSON serialization
        "confidence": float(confidence),  # Convert to Python float for JSON serialization
        "explanation": explanation,
        "matched_keywords": matched_keywords,
        "enhanced_feedback": enhanced_feedback
    }
    
    # Add learning tips if available
    if learning_tips:
        result["learning_tips"] = learning_tips
    
    return result


def batch_score_short_answers(
    student_answers: List[str],
    model_answers: List[str], 
    rubric_keywords_list: List[List[str]]
) -> List[Dict[str, Any]]:
    """
    Score multiple short answer questions in batch.
    
    Args:
        student_answers: List of student answers
        model_answers: List of corresponding model answers
        rubric_keywords_list: List of corresponding keyword lists
        
    Returns:
        List of scoring results for each answer
        
    Example:
        >>> students = ["Answer 1", "Answer 2"]
        >>> models = ["Model 1", "Model 2"]
        >>> keywords = [["key1", "key2"], ["key3", "key4"]]
        >>> results = batch_score_short_answers(students, models, keywords)
    """
    if len(student_answers) != len(model_answers) or len(student_answers) != len(rubric_keywords_list):
        raise ValueError("All input lists must have the same length")
    
    results = []
    for student, model, keywords in zip(student_answers, model_answers, rubric_keywords_list):
        result = score_short_answer(student, model, keywords)
        results.append(result)
    
    return results


# Example usage and testing
if __name__ == "__main__":
    # Test the grading service
    print("Testing grading service...")
    
    # Test cosine similarity
    a = np.array([1, 0, 0])
    b = np.array([0, 1, 0])
    c = np.array([1, 0, 0])
    
    print(f"Cosine similarity (orthogonal): {cosine(a, b):.4f}")
    print(f"Cosine similarity (identical): {cosine(a, c):.4f}")
    
    # Test keyword coverage
    answer = "To solve the equation, I need to isolate the variable by using inverse operations"
    keywords = ["isolate", "variable", "inverse", "operations", "solve"]
    coverage = keyword_coverage(answer, keywords)
    print(f"Keyword coverage: {coverage:.4f}")
    
    # Test short answer scoring
    student_answer = "To solve 2x + 3 = 7, I subtract 3 from both sides to isolate the variable x"
    model_answer = "To solve linear equations, isolate the variable by performing inverse operations on both sides"
    rubric_keywords = ["isolate", "variable", "inverse", "operations", "solve"]
    
    result = score_short_answer(student_answer, model_answer, rubric_keywords)
    
    print(f"\nShort Answer Scoring Result:")
    print(f"Score: {result['score']:.4f}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Explanation: {result['explanation']}")
    print(f"Matched Keywords: {result['matched_keywords']}")
    
    print("Grading service test completed successfully!")
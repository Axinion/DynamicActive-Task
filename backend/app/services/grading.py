import re
from typing import List, Dict, Any
from .embeddings import embed_text, cosine_similarity


def score_short_answer(
    student_answer: str, 
    model_answer: str, 
    rubric_keywords: List[str]
) -> Dict[str, Any]:
    """
    Score a short answer question using AI techniques.
    
    This is a placeholder implementation that combines:
    - Keyword matching
    - Semantic similarity
    - Length and structure analysis
    
    In a real implementation, this would use more sophisticated NLP models.
    """
    
    # Clean and normalize text
    student_clean = _clean_text(student_answer)
    model_clean = _clean_text(model_answer)
    
    # Calculate semantic similarity using embeddings
    try:
        student_embedding = embed_text(student_clean)
        model_embedding = embed_text(model_clean)
        semantic_score = cosine_similarity(student_embedding, model_embedding)
    except Exception:
        semantic_score = 0.5  # Fallback score
    
    # Calculate keyword coverage
    keyword_score = _calculate_keyword_score(student_clean, rubric_keywords)
    
    # Calculate length appropriateness (not too short, not too long)
    length_score = _calculate_length_score(student_clean, model_clean)
    
    # Calculate structure score (sentences, paragraphs, etc.)
    structure_score = _calculate_structure_score(student_clean)
    
    # Weighted combination of scores
    final_score = (
        semantic_score * 0.4 +
        keyword_score * 0.3 +
        length_score * 0.15 +
        structure_score * 0.15
    )
    
    # Generate explanation
    explanation = _generate_explanation(
        final_score, semantic_score, keyword_score, length_score, structure_score
    )
    
    # Generate feedback
    feedback = _generate_feedback(
        student_clean, model_clean, rubric_keywords, final_score
    )
    
    return {
        "score": min(max(final_score, 0.0), 1.0),  # Clamp between 0 and 1
        "explanation": explanation,
        "confidence": min(semantic_score + 0.2, 1.0),  # Confidence based on semantic similarity
        "feedback": feedback,
        "breakdown": {
            "semantic_similarity": semantic_score,
            "keyword_coverage": keyword_score,
            "length_appropriateness": length_score,
            "structure_quality": structure_score
        }
    }


def _clean_text(text: str) -> str:
    """Clean and normalize text for analysis."""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:]', '', text)
    return text.lower()


def _calculate_keyword_score(text: str, keywords: List[str]) -> float:
    """Calculate how well the text covers the required keywords."""
    if not keywords:
        return 0.5  # Neutral score if no keywords specified
    
    text_lower = text.lower()
    keyword_lower = [kw.lower() for kw in keywords]
    
    found_keywords = sum(1 for kw in keyword_lower if kw in text_lower)
    return found_keywords / len(keyword_lower)


def _calculate_length_score(student_text: str, model_text: str) -> float:
    """Calculate score based on answer length appropriateness."""
    student_len = len(student_text.split())
    model_len = len(model_text.split())
    
    if model_len == 0:
        return 0.5
    
    ratio = student_len / model_len
    
    # Optimal ratio is between 0.5 and 1.5
    if 0.5 <= ratio <= 1.5:
        return 1.0
    elif 0.3 <= ratio <= 2.0:
        return 0.8
    elif 0.2 <= ratio <= 3.0:
        return 0.6
    else:
        return 0.3


def _calculate_structure_score(text: str) -> float:
    """Calculate score based on text structure and coherence."""
    sentences = text.split('.')
    words_per_sentence = [len(s.split()) for s in sentences if s.strip()]
    
    if not words_per_sentence:
        return 0.3
    
    # Check for reasonable sentence length (not too short, not too long)
    avg_sentence_length = sum(words_per_sentence) / len(words_per_sentence)
    
    if 5 <= avg_sentence_length <= 25:
        return 1.0
    elif 3 <= avg_sentence_length <= 35:
        return 0.8
    else:
        return 0.5


def _generate_explanation(
    final_score: float, 
    semantic_score: float, 
    keyword_score: float, 
    length_score: float, 
    structure_score: float
) -> str:
    """Generate a human-readable explanation of the scoring."""
    
    if final_score >= 0.8:
        grade = "excellent"
    elif final_score >= 0.7:
        grade = "good"
    elif final_score >= 0.6:
        grade = "satisfactory"
    elif final_score >= 0.5:
        grade = "needs improvement"
    else:
        grade = "inadequate"
    
    explanation = f"The answer received a {grade} score ({final_score:.1%}). "
    
    if semantic_score >= 0.7:
        explanation += "The response demonstrates good understanding of the concepts. "
    elif semantic_score >= 0.5:
        explanation += "The response shows some understanding but could be more precise. "
    else:
        explanation += "The response may not fully address the question. "
    
    if keyword_score >= 0.7:
        explanation += "Key terms and concepts are well covered. "
    elif keyword_score >= 0.5:
        explanation += "Some key concepts are mentioned but coverage could be improved. "
    else:
        explanation += "Important key concepts appear to be missing. "
    
    return explanation.strip()


def _generate_feedback(
    student_text: str, 
    model_text: str, 
    keywords: List[str], 
    score: float
) -> str:
    """Generate constructive feedback for the student."""
    
    if score >= 0.8:
        return "Excellent work! Your answer demonstrates strong understanding of the material."
    elif score >= 0.7:
        return "Good job! Consider adding more specific examples to strengthen your response."
    elif score >= 0.6:
        return "Your answer is on the right track. Try to be more specific and include key concepts."
    elif score >= 0.5:
        return "Your response needs more detail. Consider reviewing the material and including more specific information."
    else:
        return "Please review the question and material more carefully. Your answer needs significant improvement."

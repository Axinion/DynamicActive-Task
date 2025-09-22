"""
Falcon-H1-1B-Base model service for advanced text generation and analysis.
Provides enhanced AI capabilities for feedback generation and content analysis.
"""

import os
import torch
from typing import Optional, Dict, Any, List
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

# Global model instances (lazy-loaded)
_model: Optional[AutoModelForCausalLM] = None
_tokenizer: Optional[AutoTokenizer] = None

# Model configuration
MODEL_ID = "tiiuae/Falcon-H1-1B-Base"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")


def _get_model_and_tokenizer():
    """Lazy-load the Falcon model and tokenizer."""
    global _model, _tokenizer
    
    if _model is None or _tokenizer is None:
        try:
            logger.info(f"Loading Falcon model: {MODEL_ID}")
            
            # Optional auth for private models
            token_args = {"token": HUGGINGFACE_TOKEN} if HUGGINGFACE_TOKEN else {}
            
            # Load tokenizer
            _tokenizer = AutoTokenizer.from_pretrained(
                MODEL_ID,
                trust_remote_code=True,
                **token_args
            )
            
            # Load model with better device handling
            _model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID,
                dtype=torch.bfloat16,  # Use dtype instead of deprecated torch_dtype
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True,  # Reduce memory usage
                **token_args
            )
            
            logger.info(f"Falcon model loaded successfully: {MODEL_ID}")
            
        except Exception as e:
            logger.error(f"Failed to load Falcon model: {e}")
            raise
    
    return _model, _tokenizer


def generate_feedback(
    student_answer: str,
    model_answer: str,
    question_prompt: str,
    rubric_keywords: List[str],
    score: float
) -> str:
    """
    Generate personalized feedback using Falcon-H1-1B-Base model.
    
    Args:
        student_answer: Student's submitted answer
        model_answer: Expected model answer
        question_prompt: The question that was asked
        rubric_keywords: List of important keywords
        score: The calculated score (0-1)
        
    Returns:
        Generated feedback text
    """
    try:
        model, tokenizer = _get_model_and_tokenizer()
        
        # Create a prompt for feedback generation
        prompt = f"""You are an educational AI assistant. Generate helpful feedback for a student's answer.

Question: {question_prompt}

Student Answer: {student_answer}

Model Answer: {model_answer}

Key Concepts: {', '.join(rubric_keywords)}

Score: {score:.2f}/1.0

Generate constructive feedback that:
1. Acknowledges what the student got right
2. Points out specific areas for improvement
3. Provides guidance on how to improve
4. Is encouraging and supportive

Feedback:"""

        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        # Move to same device as model with error handling
        try:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        except Exception as e:
            logger.warning(f"Device transfer failed, using CPU: {e}")
            inputs = {k: v.cpu() for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the feedback part (after "Feedback:")
        feedback_start = response.find("Feedback:")
        if feedback_start != -1:
            feedback = response[feedback_start + len("Feedback:"):].strip()
        else:
            feedback = response.strip()
        
        # Clean up the feedback
        feedback = feedback.replace(prompt, "").strip()
        
        return feedback if feedback else "Good effort! Keep practicing to improve your understanding."
        
    except Exception as e:
        logger.error(f"Error generating feedback with Falcon: {e}")
        # Fallback to simple feedback
        return _generate_fallback_feedback(student_answer, model_answer, score)


def generate_learning_tips(
    student_answer: str,
    model_answer: str,
    skill_tags: List[str],
    misconceptions: List[str] = None
) -> Dict[str, Any]:
    """
    Generate learning tips and suggestions using Falcon model.
    
    Args:
        student_answer: Student's answer
        model_answer: Model answer
        skill_tags: Relevant skill tags
        misconceptions: List of identified misconceptions
        
    Returns:
        Dictionary with tips, suggestions, and encouragement
    """
    try:
        model, tokenizer = _get_model_and_tokenizer()
        
        misconceptions_text = ", ".join(misconceptions) if misconceptions else "None identified"
        
        prompt = f"""You are an educational AI tutor. Analyze a student's answer and provide learning tips.

Student Answer: {student_answer}
Model Answer: {model_answer}
Skills: {', '.join(skill_tags)}
Misconceptions: {misconceptions_text}

Provide:
1. One encouraging praise
2. Two specific suggestions for improvement
3. One study tip

Format as JSON:
{{
    "praise": "encouraging message",
    "suggestions": ["suggestion 1", "suggestion 2"],
    "study_tip": "helpful study advice"
}}"""

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        try:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        except Exception as e:
            logger.warning(f"Device transfer failed, using CPU: {e}")
            inputs = {k: v.cpu() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.6,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON part
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            try:
                import json
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Fallback if JSON parsing fails
        return _generate_fallback_tips(student_answer, skill_tags)
        
    except Exception as e:
        logger.error(f"Error generating learning tips with Falcon: {e}")
        return _generate_fallback_tips(student_answer, skill_tags)


def analyze_misconception_pattern(
    responses: List[str],
    question_prompts: List[str],
    skill_tags: List[str]
) -> Dict[str, Any]:
    """
    Analyze patterns in student misconceptions using Falcon model.
    
    Args:
        responses: List of student responses
        question_prompts: Corresponding question prompts
        skill_tags: Relevant skill tags
        
    Returns:
        Analysis of misconception patterns
    """
    try:
        model, tokenizer = _get_model_and_tokenizer()
        
        # Combine responses for analysis
        combined_responses = " | ".join(responses[:5])  # Limit to first 5 for token limit
        combined_prompts = " | ".join(question_prompts[:5])
        
        prompt = f"""Analyze these student responses to identify common misconception patterns.

Questions: {combined_prompts}
Student Responses: {combined_responses}
Skills: {', '.join(skill_tags)}

Identify:
1. Common misconception themes
2. Missing key concepts
3. Suggested remediation strategies

Provide analysis in 2-3 sentences focusing on the most important patterns."""

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        try:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        except Exception as e:
            logger.warning(f"Device transfer failed, using CPU: {e}")
            inputs = {k: v.cpu() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.5,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract analysis part
        analysis = response.replace(prompt, "").strip()
        
        return {
            "analysis": analysis,
            "patterns_identified": len(responses),
            "model_used": MODEL_ID
        }
        
    except Exception as e:
        logger.error(f"Error analyzing misconceptions with Falcon: {e}")
        return {
            "analysis": "Unable to analyze patterns at this time.",
            "patterns_identified": 0,
            "model_used": "fallback"
        }


def _generate_fallback_feedback(student_answer: str, model_answer: str, score: float) -> str:
    """Generate simple fallback feedback when Falcon model fails."""
    if score >= 0.8:
        return "Excellent work! Your answer demonstrates a strong understanding of the concepts."
    elif score >= 0.6:
        return "Good effort! Your answer shows understanding but could be more detailed."
    elif score >= 0.4:
        return "You're on the right track. Consider reviewing the key concepts and providing more specific examples."
    else:
        return "Keep practicing! Review the material and try to include more key concepts in your answer."


def _generate_fallback_tips(student_answer: str, skill_tags: List[str]) -> Dict[str, Any]:
    """Generate simple fallback tips when Falcon model fails."""
    return {
        "praise": "Thank you for your effort in answering this question.",
        "suggestions": [
            f"Review the key concepts related to {', '.join(skill_tags[:2])}",
            "Provide more specific examples in your answers"
        ],
        "study_tip": f"Focus on understanding the fundamentals of {skill_tags[0] if skill_tags else 'this topic'}"
    }


def clear_model_cache():
    """Clear the model cache. Useful for memory management."""
    global _model, _tokenizer
    _model = None
    _tokenizer = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def get_model_info() -> Dict[str, Any]:
    """Get information about the loaded model."""
    try:
        model, tokenizer = _get_model_and_tokenizer()
        return {
            "model_id": MODEL_ID,
            "model_loaded": True,
            "device": str(model.device),
            "dtype": str(model.dtype),
            "vocab_size": tokenizer.vocab_size
        }
    except Exception as e:
        return {
            "model_id": MODEL_ID,
            "model_loaded": False,
            "error": str(e)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the Falcon service
    print("Testing Falcon service...")
    
    # Test feedback generation
    student_answer = "Plants need sunlight to grow and make food through photosynthesis."
    model_answer = "Plants use sunlight, water, and carbon dioxide to produce glucose through photosynthesis, which occurs in the chloroplasts."
    question_prompt = "Explain how plants make their own food."
    rubric_keywords = ["photosynthesis", "sunlight", "glucose", "chloroplasts"]
    score = 0.7
    
    feedback = generate_feedback(student_answer, model_answer, question_prompt, rubric_keywords, score)
    print(f"Generated feedback: {feedback}")
    
    # Test learning tips
    tips = generate_learning_tips(student_answer, model_answer, ["biology", "photosynthesis"])
    print(f"Learning tips: {tips}")
    
    print("Falcon service test completed!")

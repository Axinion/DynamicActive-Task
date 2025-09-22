"""
Misconception insights service for teachers to analyze common student errors.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime, timedelta, timezone

from ..db.models import User, Class, Assignment, Question, Submission, Response, Enrollment
from ..services.embeddings import embed_text
from ..core.config import settings


def get_time_window(period: str) -> Tuple[datetime, datetime]:
    """
    Get start and end datetime for the specified period.
    
    Args:
        period: 'week' or 'month'
        
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    end_time = datetime.now(timezone.utc)
    
    if period == "month":
        start_time = end_time - timedelta(days=30)
    else:  # default to week
        start_time = end_time - timedelta(days=7)
    
    return start_time, end_time


def get_low_scoring_responses(class_id: int, db: Session, period: str = "week") -> List[Dict]:
    """
    Fetch short-answer responses with low scores or incorrect MCQ responses within time window.
    
    Args:
        class_id: ID of the class
        db: Database session
        period: Time period ('week' or 'month')
        
    Returns:
        List of response data with student answers, scores, and metadata
    """
    # Get time window
    start_time, end_time = get_time_window(period)
    
    # Get all responses for assignments in this class within time window
    responses = db.query(Response, Question, Assignment, Submission).join(
        Question, Response.question_id == Question.id
    ).join(
        Assignment, Question.assignment_id == Assignment.id
    ).join(
        Submission, Response.submission_id == Submission.id
    ).filter(
        Assignment.class_id == class_id,
        Submission.submitted_at >= start_time,
        Submission.submitted_at <= end_time
    ).all()
    
    low_scoring_responses = []
    
    for response, question, assignment, submission in responses:
        # Determine if this response should be included
        include_response = False
        
        if question.type == "mcq":
            # For MCQ, check if it's incorrect (score < 1.0)
            score = response.teacher_score if response.teacher_score is not None else response.ai_score
            if score is not None and score < 1.0:
                include_response = True
        else:  # short answer
            # For short answer, check if score is below threshold
            score = response.teacher_score if response.teacher_score is not None else response.ai_score
            if score is not None and score < settings.SHORT_ANSWER_PASS_THRESHOLD:
                include_response = True
        
        if include_response:
            # Parse student answer (handle JSON for MCQ)
            student_answer = response.student_answer
            if question.type == "mcq" and student_answer.startswith('"') and student_answer.endswith('"'):
                try:
                    import json
                    student_answer = json.loads(student_answer)
                except:
                    pass
            
            low_scoring_responses.append({
                'response_id': response.id,
                'question_id': question.id,
                'assignment_id': assignment.id,
                'student_answer': str(student_answer),
                'question_type': question.type,
                'question_prompt': question.prompt,
                'skill_tags': question.skill_tags or [],
                'score': response.teacher_score if response.teacher_score is not None else response.ai_score,
                'assignment_title': assignment.title
            })
    
    return low_scoring_responses


def prepare_text_for_embedding(response_data: Dict) -> str:
    """
    Prepare text for embedding based on question type.
    
    Args:
        response_data: Response data dictionary
        
    Returns:
        Text to be embedded
    """
    if response_data['question_type'] == "mcq":
        # For MCQ: embed prompt + wrong chosen option
        prompt = response_data['question_prompt']
        student_answer = response_data['student_answer']
        
        # Try to get the wrong option text, fallback to prompt
        try:
            # If student answer is a JSON string, parse it
            if student_answer.startswith('"') and student_answer.endswith('"'):
                import json
                student_answer = json.loads(student_answer)
            
            # Combine prompt with wrong answer
            text_for_embedding = f"{prompt} Wrong answer: {student_answer}"
        except:
            # Fallback to just prompt
            text_for_embedding = prompt
    else:
        # For short answer: embed student answer
        text_for_embedding = response_data['student_answer']
    
    return text_for_embedding


def extract_keywords(text: str, top_k: int = 3) -> List[str]:
    """
    Extract top keywords from text using TF-IDF.
    
    Args:
        text: Input text
        top_k: Number of top keywords to return
        
    Returns:
        List of top keywords
    """
    if not text or len(text.strip()) < 3:
        return []
    
    # Clean and preprocess text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Filter out common stop words and short words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
    
    if not filtered_words:
        return []
    
    # Use simple frequency counting for small datasets
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(top_k)]


def cluster_responses(responses: List[Dict]) -> List[Dict]:
    """
    Cluster responses using KMeans on embeddings.
    
    Args:
        responses: List of response data
        
    Returns:
        List of clusters with representative examples and metadata
    """
    if len(responses) < 3:
        return []
    
    # Prepare embeddings for clustering
    embeddings = []
    valid_responses = []
    
    for response in responses:
        try:
            # Prepare text for embedding based on question type
            text_for_embedding = prepare_text_for_embedding(response)
            embedding = embed_text(text_for_embedding)
            embeddings.append(embedding)
            valid_responses.append(response)
        except Exception:
            # Skip responses that can't be embedded
            continue
    
    if len(embeddings) < 3:
        return []
    
    embeddings = np.array(embeddings)
    
    # Determine number of clusters
    n_clusters = min(3, max(1, len(embeddings) // 3))
    
    # Perform KMeans clustering
    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
    except Exception:
        return []
    
    # Group responses by cluster
    clusters = {}
    for i, (response, label) in enumerate(zip(valid_responses, cluster_labels)):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(response)
    
    # Process each cluster
    cluster_results = []
    for cluster_id, cluster_responses in clusters.items():
        if not cluster_responses:
            continue
        
        # Get representative examples (1-2 responses)
        examples = cluster_responses[:2]
        
        # Extract common keywords from all responses in cluster
        all_text = ' '.join([resp['student_answer'] for resp in cluster_responses])
        common_keywords = extract_keywords(all_text, top_k=3)
        
        # Get suggested skill tags (mode of skill tags in questions)
        all_skill_tags = []
        for resp in cluster_responses:
            all_skill_tags.extend(resp['skill_tags'])
        
        skill_tag_counts = Counter(all_skill_tags)
        suggested_skill_tags = [tag for tag, count in skill_tag_counts.most_common(3)]
        
        # Generate cluster label from top keywords
        if common_keywords:
            label = f"Misconception: {', '.join(common_keywords[:2])}"
        else:
            label = f"Misconception Cluster {cluster_id + 1}"
        
        cluster_results.append({
            'label': label,
            'examples': [
                {
                    'student_answer': ex['student_answer'],
                    'question_prompt': ex['question_prompt'],
                    'score': ex['score'],
                    'assignment_title': ex['assignment_title']
                }
                for ex in examples
            ],
            'suggested_skill_tags': suggested_skill_tags,
            'cluster_size': len(cluster_responses),
            'common_keywords': common_keywords
        })
    
    return cluster_results


def get_misconception_insights(class_id: int, db: Session, period: str = "week") -> Dict:
    """
    Get misconception insights for a class within a time period.
    
    Args:
        class_id: ID of the class
        db: Database session
        period: Time period ('week' or 'month')
        
    Returns:
        Dictionary with misconception clusters and metadata
    """
    # Get low-scoring responses within time window
    low_scoring_responses = get_low_scoring_responses(class_id, db, period)
    
    if len(low_scoring_responses) < 3:
        start_time, end_time = get_time_window(period)
        return {
            'class_id': class_id,
            'period': period,
            'time_window': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'total_items': len(low_scoring_responses),
            'clusters': [],
            'message': 'Not enough data for misconception analysis. Need at least 3 low-scoring responses.'
        }
    
    # Cluster the responses
    clusters = cluster_responses(low_scoring_responses)
    
    # Get class info
    class_info = db.query(Class).filter(Class.id == class_id).first()
    start_time, end_time = get_time_window(period)
    
    return {
        'class_id': class_id,
        'class_name': class_info.name if class_info else 'Unknown Class',
        'period': period,
        'time_window': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        },
        'total_items': len(low_scoring_responses),
        'clusters': clusters,
            'analysis_summary': {
                'total_clusters': len(clusters),
                'threshold_used': settings.SHORT_ANSWER_PASS_THRESHOLD,
                'analysis_type': 'KMeans clustering on response embeddings'
            }
    }

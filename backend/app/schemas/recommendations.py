from pydantic import BaseModel
from typing import List, Optional


class LessonRecommendation(BaseModel):
    id: int
    title: str
    content: str
    class_name: str
    why: str  # Explanation of why this lesson is recommended
    skill_tags: List[str]
    difficulty_score: Optional[float] = None


class RecommendationResponse(BaseModel):
    student_id: int
    recommendations: List[LessonRecommendation]
    based_on: str  # What the recommendations are based on

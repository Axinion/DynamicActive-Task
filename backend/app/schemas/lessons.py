from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class LessonCreate(BaseModel):
    class_id: int
    title: str
    content: str
    skill_tags: List[str] = []


class LessonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    class_id: int
    title: str
    content: str
    skill_tags: List[str]
    created_at: datetime


class LessonResponse(LessonRead):
    """Alias for backward compatibility"""
    pass


class LessonWithClass(LessonRead):
    class_name: str

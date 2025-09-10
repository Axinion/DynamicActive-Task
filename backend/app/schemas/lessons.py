from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class LessonCreate(BaseModel):
    class_id: int
    title: str
    content: str
    skill_tags: Optional[List[str]] = []


class LessonResponse(BaseModel):
    id: int
    class_id: int
    title: str
    content: str
    skill_tags: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True


class LessonWithClass(LessonResponse):
    class_name: str

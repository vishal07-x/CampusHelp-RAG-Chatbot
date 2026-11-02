from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    message_id: str
    rating: int = Field(..., description="1 for helpful, -1 for unhelpful")
    feedback_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    message_id: str
    rating: int
    feedback_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

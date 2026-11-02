from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    chunk_id: str
    relevance_score: float
    excerpt: str
    department: Optional[str] = "General"
    category: Optional[str] = "General"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    department_filter: Optional[str] = None
    category_filter: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    citations: List[Citation] = []
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    token_usage: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    citations: Optional[List[Citation]] = None
    latency_ms: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

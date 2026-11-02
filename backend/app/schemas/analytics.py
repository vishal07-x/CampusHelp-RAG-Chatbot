from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    total_users: int
    avg_retrieval_latency_ms: float
    avg_generation_latency_ms: float
    avg_total_latency_ms: float
    positive_feedback_count: int
    negative_feedback_count: int
    feedback_satisfaction_rate: float
    category_distribution: Dict[str, int]
    department_distribution: Dict[str, int]


class QueryLogItem(BaseModel):
    id: str
    user_id: Optional[str] = None
    query_text: str
    answer_text: Optional[str] = None
    retrieved_sources: Optional[List[Dict[str, Any]]] = None
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class QueryLogsResponse(BaseModel):
    total: int
    logs: List[QueryLogItem]

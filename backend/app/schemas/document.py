from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    department: str
    category: str
    total_pages: int
    total_chunks: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class IngestionProgressResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    total_pages: int
    total_chunks: int
    message: str

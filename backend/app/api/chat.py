from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Conversation, ChatMessage, User
from app.schemas.chat import (
    ChatRequest, ChatResponse, ConversationResponse,
    ConversationDetailResponse, MessageResponse, Citation
)
from app.api.deps import get_optional_user, get_current_user
from app.services.rag.pipeline import rag_pipeline
from app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def handle_chat_message(
    chat_in: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Submits a user question to the CampusHelp RAG pipeline.
    Retrieves relevant document chunks, performs reranking, and generates grounded answer with citations.
    """
    user_id = current_user.id if current_user else None

    # Retrieve or create conversation
    conv = None
    if chat_in.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == chat_in.conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    else:
        # Create a new conversation with auto-generated title based on first query
        conv_title = chat_in.message[:40] + ("..." if len(chat_in.message) > 40 else "")
        conv = Conversation(
            user_id=user_id,
            title=conv_title
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Fetch recent conversation history (last 4 messages) for multi-turn context
    recent_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(4)
        .all()
    )
    history = []
    for msg in reversed(recent_messages):
        history.append({
            "role": "user" if msg.sender == "user" else "assistant",
            "content": msg.content
        })

    # Save user message to database
    user_msg = ChatMessage(
        conversation_id=conv.id,
        sender="user",
        content=chat_in.message
    )
    db.add(user_msg)
    db.commit()

    # Run RAG Pipeline
    rag_result = rag_pipeline.answer_query(
        query=chat_in.message,
        department_filter=chat_in.department_filter,
        category_filter=chat_in.category_filter,
        conversation_history=history,
        user_id=user_id,
        db=db
    )

    # Save assistant response to database
    citations_data = rag_result.get("citations", [])
    assistant_msg = ChatMessage(
        conversation_id=conv.id,
        sender="assistant",
        content=rag_result["answer"],
        citations=citations_data,
        latency_ms=rag_result["total_latency_ms"],
        token_usage=rag_result["token_usage"]
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # Format output citations
    citation_objs = [
        Citation(
            document_id=c.get("document_id", ""),
            document_name=c.get("document_name", ""),
            page_number=c.get("page_number", 1),
            chunk_id=c.get("chunk_id", ""),
            relevance_score=c.get("relevance_score", 0.0),
            excerpt=c.get("excerpt", ""),
            department=c.get("department", "General"),
            category=c.get("category", "General")
        )
        for c in citations_data
    ]

    return ChatResponse(
        conversation_id=conv.id,
        message_id=assistant_msg.id,
        answer=rag_result["answer"],
        citations=citation_objs,
        retrieval_latency_ms=rag_result["retrieval_latency_ms"],
        generation_latency_ms=rag_result["generation_latency_ms"],
        total_latency_ms=rag_result["total_latency_ms"],
        token_usage=rag_result["token_usage"]
    )


@router.get("/conversations", response_model=List[ConversationResponse])
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    res = []
    for c in conversations:
        res.append(ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages)
        ))
    return res


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    formatted_messages = []
    for msg in conv.messages:
        formatted_messages.append(MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender=msg.sender,
            content=msg.content,
            citations=msg.citations,
            latency_ms=msg.latency_ms,
            created_at=msg.created_at
        ))

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    db.delete(conv)
    db.commit()
    return None

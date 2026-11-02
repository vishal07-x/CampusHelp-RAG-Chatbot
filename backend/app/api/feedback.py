from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import UserFeedback, ChatMessage, User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.api.deps import get_optional_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    fb_in: FeedbackCreate,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    msg = db.query(ChatMessage).filter(ChatMessage.id == fb_in.message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")

    user_id = current_user.id if current_user else None

    # Check if existing feedback for this message by user
    existing_fb = db.query(UserFeedback).filter(
        UserFeedback.message_id == fb_in.message_id,
        UserFeedback.user_id == user_id
    ).first()

    if existing_fb:
        existing_fb.rating = fb_in.rating
        existing_fb.feedback_text = fb_in.feedback_text
        db.commit()
        db.refresh(existing_fb)
        return existing_fb

    new_fb = UserFeedback(
        message_id=fb_in.message_id,
        user_id=user_id,
        rating=fb_in.rating,
        feedback_text=fb_in.feedback_text
    )
    db.add(new_fb)
    db.commit()
    db.refresh(new_fb)
    return new_fb

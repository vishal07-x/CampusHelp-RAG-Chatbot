from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Document, DocumentChunk, QueryLog, User, UserFeedback


class AnalyticsService:
    @staticmethod
    def get_summary(db: Session) -> Dict[str, Any]:
        total_docs = db.query(Document).filter(Document.status == "INDEXED").count()
        total_chunks = db.query(DocumentChunk).count()
        total_queries = db.query(QueryLog).count()
        total_users = db.query(User).count()

        # Latency averages
        latencies = db.query(
            func.avg(QueryLog.retrieval_latency_ms),
            func.avg(QueryLog.generation_latency_ms),
            func.avg(QueryLog.total_latency_ms)
        ).first()

        avg_retrieval = round(float(latencies[0] or 0.0), 2)
        avg_generation = round(float(latencies[1] or 0.0), 2)
        avg_total = round(float(latencies[2] or 0.0), 2)

        # Feedback stats
        positive_feedback = db.query(UserFeedback).filter(UserFeedback.rating > 0).count()
        negative_feedback = db.query(UserFeedback).filter(UserFeedback.rating < 0).count()
        total_feedback = positive_feedback + negative_feedback
        satisfaction_rate = round((positive_feedback / total_feedback * 100), 1) if total_feedback > 0 else 100.0

        # Distribution by category & department
        dept_counts = db.query(Document.department, func.count(Document.id)).filter(Document.status == "INDEXED").group_by(Document.department).all()
        cat_counts = db.query(Document.category, func.count(Document.id)).filter(Document.status == "INDEXED").group_by(Document.category).all()

        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "total_queries": total_queries,
            "total_users": total_users,
            "avg_retrieval_latency_ms": avg_retrieval,
            "avg_generation_latency_ms": avg_generation,
            "avg_total_latency_ms": avg_total,
            "positive_feedback_count": positive_feedback,
            "negative_feedback_count": negative_feedback,
            "feedback_satisfaction_rate": satisfaction_rate,
            "department_distribution": {d[0]: d[1] for d in dept_counts},
            "category_distribution": {c[0]: c[1] for c in cat_counts}
        }

    @staticmethod
    def get_logs(db: Session, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        total = db.query(QueryLog).count()
        logs = db.query(QueryLog).order_by(QueryLog.created_at.desc()).offset(offset).limit(limit).all()
        return {
            "total": total,
            "logs": logs
        }


analytics_service = AnalyticsService()

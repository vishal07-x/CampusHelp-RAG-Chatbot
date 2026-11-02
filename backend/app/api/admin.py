from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas.analytics import AnalyticsSummary, QueryLogsResponse, QueryLogItem
from app.api.deps import get_current_admin
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/analytics", response_model=AnalyticsSummary)
def get_system_analytics(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint: Returns global platform usage metrics, latency, and feedback statistics."""
    return analytics_service.get_summary(db)


@router.get("/logs", response_model=QueryLogsResponse)
def get_query_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint: Returns comprehensive query logs with latency, retrieved documents, and status."""
    res = analytics_service.get_logs(db, limit=limit, offset=offset)
    formatted_logs = [QueryLogItem.model_validate(l) for l in res["logs"]]
    return QueryLogsResponse(
        total=res["total"],
        logs=formatted_logs
    )

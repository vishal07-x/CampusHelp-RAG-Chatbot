from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.services.rag.vector_db import VectorDBService

router = APIRouter(tags=["System Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness probe: verifies that the web service is alive and accepting traffic."""
    return {
        "status": "healthy",
        "service": "CampusHelp RAG API",
        "version": "1.0.0"
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: validates database and vector database connections."""
    checks = {
        "database": False,
        "vector_database": False
    }

    # 1. Check SQL Database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        checks["database_error"] = str(e)

    # 2. Check Vector Database
    try:
        vdb = VectorDBService()
        vdb.client.get_collections()
        checks["vector_database"] = True
    except Exception as e:
        checks["vector_database_error"] = str(e)

    is_ready = checks["database"] and checks["vector_database"]
    http_status = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "ready": is_ready,
            "components": checks
        }
    )

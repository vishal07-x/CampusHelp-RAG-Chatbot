from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document, User
from app.schemas.document import DocumentResponse, DocumentListResponse, IngestionProgressResponse
from app.api.deps import get_current_admin, get_optional_user
from app.services.ingestion_service import ingestion_service
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=List[IngestionProgressResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    department: str = Form("General"),
    category: str = Form("General"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint: Uploads and indexes one or more college PDF documents into Qdrant & database.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    results = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            results.append(IngestionProgressResponse(
                document_id="N/A",
                filename=file.filename,
                status="FAILED",
                total_pages=0,
                total_chunks=0,
                message="Rejected: Only PDF (.pdf) files are supported."
            ))
            continue

        try:
            content = await file.read()
            res = ingestion_service.ingest_pdf(
                file_bytes=content,
                filename=file.filename,
                department=department,
                category=category,
                db=db
            )
            results.append(IngestionProgressResponse(
                document_id=res["document_id"],
                filename=res["filename"],
                status=res["status"],
                total_pages=res["total_pages"],
                total_chunks=res["total_chunks"],
                message=res["message"]
            ))
        except ValueError as ve:
            results.append(IngestionProgressResponse(
                document_id="N/A",
                filename=file.filename,
                status="FAILED",
                total_pages=0,
                total_chunks=0,
                message=str(ve)
            ))
        except Exception as e:
            logger.error(f"Error processing upload for {file.filename}: {e}")
            results.append(IngestionProgressResponse(
                document_id="N/A",
                filename=file.filename,
                status="FAILED",
                total_pages=0,
                total_chunks=0,
                message=f"Ingestion failed: {str(e)}"
            ))

    return results


@router.get("", response_model=DocumentListResponse)
def list_documents(
    department: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists all registered documents with metadata and indexing status."""
    query = db.query(Document)

    if department and department.lower() != "all":
        query = query.filter(Document.department == department)
    if category and category.lower() != "all":
        query = query.filter(Document.category == category)
    if status_filter:
        query = query.filter(Document.status == status_filter.upper())

    docs = query.order_by(Document.created_at.desc()).all()
    return DocumentListResponse(
        total=len(docs),
        documents=[DocumentResponse.model_validate(d) for d in docs]
    )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint: Deletes a document and purges its vector points and chunks."""
    try:
        success = ingestion_service.delete_document(document_id, db=db)
        return {"status": "success", "message": f"Document {document_id} deleted successfully."}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/{document_id}/reindex", response_model=IngestionProgressResponse)
def reindex_document(
    document_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint: Re-indexes an existing document."""
    try:
        res = ingestion_service.reindex_document(document_id, db=db)
        return IngestionProgressResponse(
            document_id=res["document_id"],
            filename=res["filename"],
            status=res["status"],
            total_pages=res["total_pages"],
            total_chunks=res["total_chunks"],
            message=res["message"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to re-index document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Re-indexing failed: {str(e)}")

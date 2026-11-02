import os
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.models import Document, DocumentChunk
from app.services.rag.pdf_extractor import PDFExtractor, PDFExtractionError
from app.services.rag.chunker import TextChunker
from app.services.rag.pipeline import rag_pipeline


class IngestionService:
    def __init__(self):
        self.extractor = PDFExtractor()
        self.chunker = TextChunker()
        self.pipeline = rag_pipeline

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Calculates SHA-256 hash of file content to detect duplicates."""
        return hashlib.sha256(file_bytes).hexdigest()

    def warm_up_bm25_from_db(self, db: Session):
        """Loads all existing indexed chunks from DB into the in-memory BM25 index on startup."""
        try:
            chunks = db.query(DocumentChunk).join(Document).filter(Document.status == "INDEXED").all()
            if not chunks:
                logger.info("No existing indexed document chunks found in database.")
                return

            chunk_dicts = []
            for c in chunks:
                chunk_dicts.append({
                    "document_id": c.document_id,
                    "document_name": c.document.filename if c.document else "Document",
                    "chunk_index": c.chunk_index,
                    "page_number": c.page_number,
                    "content": c.content,
                    "token_count": c.token_count,
                    "department": c.document.department if c.document else "General",
                    "category": c.document.category if c.document else "General",
                    "qdrant_point_id": c.qdrant_point_id
                })

            self.pipeline.bm25_retriever.index_chunks(chunk_dicts)
            logger.info(f"Loaded {len(chunk_dicts)} chunks into BM25 index.")
        except Exception as e:
            logger.error(f"Error warming up BM25 index from DB: {e}")

    def ingest_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        department: str = "General",
        category: str = "General",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Processes and indexes a newly uploaded PDF document.
        """
        # 1. Validation
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF documents (.pdf) are accepted.")

        file_size = len(file_bytes)
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ValueError(f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB}MB.")

        # 2. Check duplicates
        file_hash = self.calculate_file_hash(file_bytes)
        if db:
            existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
            if existing_doc:
                raise ValueError(
                    f"Duplicate document detected! '{existing_doc.original_name}' (ID: {existing_doc.id}) "
                    f"has the exact same content."
                )

        # 3. Save file to disk
        safe_filename = f"{file_hash[:12]}_{filename}"
        file_path = Path(settings.UPLOAD_DIRECTORY) / safe_filename
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # 4. Create Document record in DB with PENDING status
        doc_record = None
        if db:
            doc_record = Document(
                filename=safe_filename,
                original_name=filename,
                file_path=str(file_path),
                file_size=file_size,
                file_hash=file_hash,
                department=department,
                category=category,
                status="PENDING"
            )
            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)
            doc_id = doc_record.id
        else:
            import uuid
            doc_id = str(uuid.uuid4())

        # 5. Extract, Chunk, Embed, Index
        try:
            # Extract
            pages_data = self.extractor.extract_from_file(str(file_path))
            total_pages = len(pages_data)

            # Chunk
            chunks_data = self.chunker.chunk_pages(
                pages_data=pages_data,
                document_id=doc_id,
                document_name=filename,
                department=department,
                category=category
            )

            if not chunks_data:
                raise ValueError("Could not extract any meaningful text chunks from this document.")

            # Embed
            texts = [c["content"] for c in chunks_data]
            embeddings = self.pipeline.embedding_service.get_embeddings(texts)

            # Index into Qdrant
            point_ids = self.pipeline.vector_db.upsert_chunks(chunks_data, embeddings)

            # Index into BM25
            self.pipeline.bm25_retriever.add_chunks(chunks_data)

            # Save Chunks to DB
            if db and doc_record:
                for chunk, point_id in zip(chunks_data, point_ids):
                    chunk_row = DocumentChunk(
                        document_id=doc_id,
                        chunk_index=chunk["chunk_index"],
                        page_number=chunk["page_number"],
                        content=chunk["content"],
                        token_count=chunk["token_count"],
                        qdrant_point_id=point_id
                    )
                    db.add(chunk_row)

                doc_record.total_pages = total_pages
                doc_record.total_chunks = len(chunks_data)
                doc_record.status = "INDEXED"
                doc_record.error_message = None
                db.commit()
                db.refresh(doc_record)

            return {
                "document_id": doc_id,
                "filename": filename,
                "status": "INDEXED",
                "total_pages": total_pages,
                "total_chunks": len(chunks_data),
                "message": f"Successfully indexed '{filename}' with {len(chunks_data)} chunks across {total_pages} pages."
            }

        except Exception as e:
            logger.error(f"Ingestion failed for document {filename}: {e}")
            if db and doc_record:
                doc_record.status = "FAILED"
                doc_record.error_message = str(e)
                db.commit()
            raise

    def reindex_document(self, document_id: str, db: Session) -> Dict[str, Any]:
        """
        Re-indexes an existing document: cleans old points/chunks, re-chunks, and re-embeds.
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found.")

        if not os.path.exists(doc.file_path):
            raise FileNotFoundError(f"Document file missing on disk: {doc.file_path}")

        # 1. Clean Qdrant points
        self.pipeline.vector_db.delete_document_points(document_id)

        # 2. Clean BM25 entries
        self.pipeline.bm25_retriever.remove_document_chunks(document_id)

        # 3. Clean DB chunks
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        db.commit()

        # 4. Re-run ingestion on saved file
        try:
            pages_data = self.extractor.extract_from_file(doc.file_path)
            total_pages = len(pages_data)

            chunks_data = self.chunker.chunk_pages(
                pages_data=pages_data,
                document_id=doc.id,
                document_name=doc.original_name,
                department=doc.department,
                category=doc.category
            )

            texts = [c["content"] for c in chunks_data]
            embeddings = self.pipeline.embedding_service.get_embeddings(texts)
            point_ids = self.pipeline.vector_db.upsert_chunks(chunks_data, embeddings)
            self.pipeline.bm25_retriever.add_chunks(chunks_data)

            for chunk, point_id in zip(chunks_data, point_ids):
                chunk_row = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=chunk["chunk_index"],
                    page_number=chunk["page_number"],
                    content=chunk["content"],
                    token_count=chunk["token_count"],
                    qdrant_point_id=point_id
                )
                db.add(chunk_row)

            doc.total_pages = total_pages
            doc.total_chunks = len(chunks_data)
            doc.status = "INDEXED"
            doc.error_message = None
            db.commit()
            db.refresh(doc)

            return {
                "document_id": doc.id,
                "filename": doc.original_name,
                "status": "INDEXED",
                "total_pages": total_pages,
                "total_chunks": len(chunks_data),
                "message": f"Successfully re-indexed '{doc.original_name}' with {len(chunks_data)} chunks."
            }

        except Exception as e:
            doc.status = "FAILED"
            doc.error_message = str(e)
            db.commit()
            raise

    def delete_document(self, document_id: str, db: Session) -> bool:
        """Deletes a document completely from Qdrant, BM25, Database, and Disk."""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found.")

        # 1. Remove from Qdrant
        self.pipeline.vector_db.delete_document_points(document_id)

        # 2. Remove from BM25
        self.pipeline.bm25_retriever.remove_document_chunks(document_id)

        # 3. Remove physical file
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception as e:
                logger.warning(f"Could not remove file {doc.file_path}: {e}")

        # 4. Remove from DB (chunks cascade deleted)
        db.delete(doc)
        db.commit()
        return True


ingestion_service = IngestionService()

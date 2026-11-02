import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointStruct
from app.core.config import settings
from app.core.logging import logger


class VectorDBService:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.EMBEDDING_DIMENSION
        self.client = self._init_client()
        self._ensure_collection_exists()

    def _init_client(self) -> QdrantClient:
        # 1. Try remote Qdrant server if configured
        if settings.QDRANT_URL:
            try:
                client = QdrantClient(url=settings.QDRANT_URL, timeout=5)
                # Test connectivity
                client.get_collections()
                logger.info(f"Connected to remote Qdrant at {settings.QDRANT_URL}")
                return client
            except Exception as e:
                logger.warning(f"Could not connect to QDRANT_URL ({settings.QDRANT_URL}): {e}")

        # 2. Try localhost Qdrant port
        try:
            client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=2)
            client.get_collections()
            logger.info(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            return client
        except Exception:
            pass

        # 3. Fallback to embedded local path or in-memory
        local_path = settings.QDRANT_LOCAL_PATH
        os.makedirs(local_path, exist_ok=True)
        try:
            client = QdrantClient(path=local_path)
            logger.info(f"Using local embedded Qdrant database at {local_path}")
            return client
        except Exception as e:
            logger.warning(f"Failed to use local path ({e}), initializing in-memory Qdrant.")
            return QdrantClient(":memory:")

    def _ensure_collection_exists(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name} (dim: {self.vector_size})")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                # Create payload indexes for efficient filtering
                for field_name in ["document_id", "department", "category"]:
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field_name,
                            field_schema=models.PayloadSchemaType.KEYWORD
                        )
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """
        Inserts or updates chunks in Qdrant.
        Returns list of point IDs.
        """
        if not chunks or not embeddings or len(chunks) != len(embeddings):
            return []

        points = []
        point_ids = []

        import uuid
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            point_id = chunk.get("qdrant_point_id")
            if not point_id:
                point_id = str(uuid.uuid4())
                chunk["qdrant_point_id"] = point_id
            else:
                try:
                    uuid.UUID(str(point_id))
                except (ValueError, AttributeError):
                    point_id = str(uuid.uuid4())
                    chunk["qdrant_point_id"] = point_id

            point_ids.append(point_id)

            payload = {
                "document_id": chunk["document_id"],
                "document_name": chunk["document_name"],
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk["page_number"],
                "content": chunk["content"],
                "token_count": chunk.get("token_count", 0),
                "department": chunk.get("department", "General"),
                "category": chunk.get("category", "General")
            }

            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))

        # Batch upsert
        batch_size = 64
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

        return point_ids

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        department_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search with optional metadata filters.
        """
        conditions = []

        if department_filter and department_filter.lower() != "all":
            conditions.append(FieldCondition(key="department", match=MatchValue(value=department_filter)))

        if category_filter and category_filter.lower() != "all":
            conditions.append(FieldCondition(key="category", match=MatchValue(value=category_filter)))

        if document_id:
            conditions.append(FieldCondition(key="document_id", match=MatchValue(value=document_id)))

        query_filter = Filter(must=conditions) if conditions else None

        try:
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    query_filter=query_filter
                )
                results = response.points
            else:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=query_filter
                )

            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "point_id": str(hit.id),
                    "score": float(hit.score),
                    "document_id": hit.payload.get("document_id"),
                    "document_name": hit.payload.get("document_name"),
                    "page_number": hit.payload.get("page_number", 1),
                    "chunk_index": hit.payload.get("chunk_index", 0),
                    "content": hit.payload.get("content", ""),
                    "department": hit.payload.get("department", "General"),
                    "category": hit.payload.get("category", "General")
                })

            return formatted_results
        except Exception as e:
            logger.error(f"Vector search failed in Qdrant: {e}")
            return []

    def delete_document_points(self, document_id: str) -> bool:
        """Deletes all indexed vectors associated with a document_id."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="document_id",
                                match=MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete points for document {document_id}: {e}")
            return False

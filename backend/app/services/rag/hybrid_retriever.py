import time
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vector_db import VectorDBService
from app.services.rag.bm25_retriever import BM25RetrieverService
from app.services.rag.reranker import CrossEncoderReranker


class HybridRetrieverService:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_db: Optional[VectorDBService] = None,
        bm25_retriever: Optional[BM25RetrieverService] = None,
        reranker: Optional[CrossEncoderReranker] = None
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_db = vector_db or VectorDBService()
        self.bm25_retriever = bm25_retriever or BM25RetrieverService()
        self.reranker = reranker or CrossEncoderReranker()
        self.rrf_k = 60  # Standard Reciprocal Rank Fusion constant

    @staticmethod
    def preprocess_query(query: str) -> str:
        """Preprocesses user query by removing excessive whitespace and common query noise."""
        if not query:
            return ""
        cleaned = " ".join(query.strip().split())
        return cleaned

    def retrieve(
        self,
        query: str,
        department_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        top_candidates: int = None,
        rerank_top_k: int = None
    ) -> Dict[str, Any]:
        """
        Executes complete hybrid retrieval + reranking pipeline:
        1. Query preprocessing
        2. Semantic vector search (top candidates)
        3. BM25 keyword search (top candidates)
        4. Reciprocal Rank Fusion (RRF)
        5. Cross-Encoder reranking (rerank_top_k)
        """
        top_candidates = top_candidates or settings.TOP_K_CANDIDATES
        rerank_top_k = rerank_top_k or settings.RERANK_TOP_K

        t_start = time.perf_counter()
        clean_query = self.preprocess_query(query)

        # Step 1: Semantic Vector Search
        query_vector = self.embedding_service.get_embedding(clean_query)
        vector_results = self.vector_db.search(
            query_vector=query_vector,
            top_k=top_candidates,
            department_filter=department_filter,
            category_filter=category_filter
        )

        # Step 2: BM25 Keyword Search
        bm25_results = self.bm25_retriever.search(
            query=clean_query,
            top_k=top_candidates,
            department_filter=department_filter,
            category_filter=category_filter
        )

        t_retrieval = time.perf_counter()
        retrieval_latency_ms = (t_retrieval - t_start) * 1000

        # Step 3: Reciprocal Rank Fusion (RRF)
        # Unique key for chunk: (document_id, chunk_index) or point_id
        chunk_map: Dict[str, Dict[str, Any]] = {}
        rrf_scores: Dict[str, float] = {}

        # Process vector ranks
        for rank, item in enumerate(vector_results, start=1):
            key = f"{item['document_id']}_{item['chunk_index']}"
            chunk_map[key] = item
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (self.rrf_k + rank))

        # Process BM25 ranks
        for rank, item in enumerate(bm25_results, start=1):
            key = f"{item['document_id']}_{item['chunk_index']}"
            if key not in chunk_map:
                chunk_map[key] = item
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort candidates by combined RRF score
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        fused_candidates = []
        for k in sorted_keys[:top_candidates]:
            candidate = chunk_map[k]
            candidate["rrf_score"] = rrf_scores[k]
            fused_candidates.append(candidate)

        # Step 4: Cross-Encoder Reranking
        t_rerank_start = time.perf_counter()
        reranked_chunks = self.reranker.rerank(clean_query, fused_candidates, top_k=rerank_top_k)
        t_rerank_end = time.perf_counter()
        rerank_latency_ms = (t_rerank_end - t_rerank_start) * 1000

        return {
            "query": clean_query,
            "chunks": reranked_chunks,
            "vector_candidates_count": len(vector_results),
            "bm25_candidates_count": len(bm25_results),
            "fused_count": len(fused_candidates),
            "retrieval_latency_ms": round(retrieval_latency_ms, 2),
            "rerank_latency_ms": round(rerank_latency_ms, 2)
        }

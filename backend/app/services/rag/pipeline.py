import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vector_db import VectorDBService
from app.services.rag.bm25_retriever import BM25RetrieverService
from app.services.rag.reranker import CrossEncoderReranker
from app.services.rag.hybrid_retriever import HybridRetrieverService
from app.services.rag.llm_generator import LLMGenerator
from app.db.models import QueryLog


class RAGPipeline:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_db: Optional[VectorDBService] = None,
        bm25_retriever: Optional[BM25RetrieverService] = None,
        reranker: Optional[CrossEncoderReranker] = None,
        llm_generator: Optional[LLMGenerator] = None
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_db = vector_db or VectorDBService()
        self.bm25_retriever = bm25_retriever or BM25RetrieverService()
        self.reranker = reranker or CrossEncoderReranker()
        
        self.retriever = HybridRetrieverService(
            embedding_service=self.embedding_service,
            vector_db=self.vector_db,
            bm25_retriever=self.bm25_retriever,
            reranker=self.reranker
        )
        self.llm_generator = llm_generator or LLMGenerator()

    def answer_query(
        self,
        query: str,
        department_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end RAG query flow:
        1. Hybrid Vector + BM25 retrieval
        2. Cross-encoder reranking
        3. Formats structured citation objects
        4. Context-grounded LLM generation
        5. Logs metrics to database
        """
        t_total_start = time.perf_counter()

        # Step 1 & 2: Retrieval and Reranking
        retrieval_output = self.retriever.retrieve(
            query=query,
            department_filter=department_filter,
            category_filter=category_filter
        )
        selected_chunks = retrieval_output.get("chunks", [])

        # Step 3: Format Citations
        citations = []
        for c in selected_chunks:
            # Build excerpt snippet (first 150 chars)
            raw_content = c.get("content", "")
            excerpt = (raw_content[:150] + "...") if len(raw_content) > 150 else raw_content

            citations.append({
                "document_id": c.get("document_id", ""),
                "document_name": c.get("document_name", "Official Document"),
                "page_number": c.get("page_number", 1),
                "chunk_id": str(c.get("chunk_index", 0)),
                "relevance_score": round(c.get("rerank_score", c.get("score", 0.0)), 4),
                "excerpt": excerpt,
                "department": c.get("department", "General"),
                "category": c.get("category", "General")
            })

        # Step 4: Generation
        answer, gen_latency_ms, token_usage = self.llm_generator.generate(
            query=query,
            chunks=selected_chunks,
            conversation_history=conversation_history
        )

        t_total_end = time.perf_counter()
        total_latency_ms = (t_total_end - t_total_start) * 1000

        result = {
            "query": query,
            "answer": answer,
            "citations": citations,
            "retrieval_latency_ms": retrieval_output.get("retrieval_latency_ms", 0.0),
            "rerank_latency_ms": retrieval_output.get("rerank_latency_ms", 0.0),
            "generation_latency_ms": round(gen_latency_ms, 2),
            "total_latency_ms": round(total_latency_ms, 2),
            "token_usage": token_usage,
            "chunks_used": len(selected_chunks)
        }

        # Step 5: Log to database if db session provided
        if db is not None:
            try:
                log_entry = QueryLog(
                    user_id=user_id,
                    query_text=query,
                    answer_text=answer,
                    retrieved_sources=citations,
                    retrieval_latency_ms=result["retrieval_latency_ms"],
                    rerank_latency_ms=result["rerank_latency_ms"],
                    generation_latency_ms=result["generation_latency_ms"],
                    total_latency_ms=result["total_latency_ms"],
                    token_usage=token_usage,
                    status="SUCCESS"
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to record QueryLog to database: {e}")
                db.rollback()

        return result


# Global singleton instance for app-wide use
rag_pipeline = RAGPipeline()

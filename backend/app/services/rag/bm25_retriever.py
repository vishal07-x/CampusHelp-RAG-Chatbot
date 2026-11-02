import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from app.core.logging import logger


class BM25RetrieverService:
    def __init__(self):
        self.bm25: Optional[BM25Okapi] = None
        self.corpus_chunks: List[Dict[str, Any]] = []

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple, fast regex tokenizer: lowercases, removes punctuation, keeps alphanumeric terms."""
        if not text:
            return []
        tokens = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        return tokens

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """Builds or replaces the in-memory BM25 index from a list of chunk dicts."""
        self.corpus_chunks = chunks
        if not chunks:
            self.bm25 = None
            return

        tokenized_corpus = [self.tokenize(chunk["content"]) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built with {len(chunks)} chunks.")

    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        """Appends new chunks and rebuilds the BM25 index."""
        self.corpus_chunks.extend(new_chunks)
        self.index_chunks(self.corpus_chunks)

    def remove_document_chunks(self, document_id: str):
        """Removes chunks belonging to a document and rebuilds index."""
        self.corpus_chunks = [c for c in self.corpus_chunks if c.get("document_id") != document_id]
        self.index_chunks(self.corpus_chunks)

    def search(
        self,
        query: str,
        top_k: int = 10,
        department_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k chunks using BM25 keyword matching.
        """
        if not self.bm25 or not self.corpus_chunks:
            return []

        tokens = self.tokenize(query)
        if not tokens:
            return []

        doc_scores = self.bm25.get_scores(tokens)
        token_set = set(tokens)

        scored_candidates = []
        for idx, score in enumerate(doc_scores):
            chunk = self.corpus_chunks[idx]
            chunk_tokens = set(self.tokenize(chunk.get("content", "")))
            overlap = token_set & chunk_tokens

            # If neither BM25 score > 0 nor any keyword overlap, skip
            if score <= 0.0 and not overlap:
                continue

            # In small corpora, rank_bm25 IDF can be 0 or negative; blend with keyword overlap
            adjusted_score = float(score) if score > 0 else (len(overlap) / max(1, len(token_set)))

            # Department filter
            if department_filter and department_filter.lower() != "all":
                if chunk.get("department", "General").lower() != department_filter.lower():
                    continue

            # Category filter
            if category_filter and category_filter.lower() != "all":
                if chunk.get("category", "General").lower() != category_filter.lower():
                    continue

            scored_candidates.append({
                "score": float(adjusted_score),
                "document_id": chunk.get("document_id"),
                "document_name": chunk.get("document_name"),
                "page_number": chunk.get("page_number", 1),
                "chunk_index": chunk.get("chunk_index", 0),
                "content": chunk.get("content", ""),
                "department": chunk.get("department", "General"),
                "category": chunk.get("category", "General"),
                "point_id": chunk.get("qdrant_point_id", "")
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:top_k]

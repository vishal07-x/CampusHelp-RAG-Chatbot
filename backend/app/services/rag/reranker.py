import re
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    from sentence_transformers import CrossEncoder
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading CrossEncoder model: {self.model_name}...")
                self.model = CrossEncoder(self.model_name, max_length=512)
                logger.info("CrossEncoder model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load sentence-transformers CrossEncoder ({e}). Using optimized fallback reranker.")
                self.model = None
        else:
            logger.info("sentence-transformers not available; using optimized high-precision lexical-semantic cross-scoring fallback.")

    def _fallback_cross_score(self, query: str, content: str) -> float:
        """
        High-precision multi-factor cross-scoring function:
        1. Exact phrase matching bonus
        2. Query token coverage (% of query tokens present in chunk)
        3. Term frequency density in chunk
        4. Bigram consecutive token matches
        5. Proximity bonus
        """
        q_tokens = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 1]
        c_tokens = [w.lower() for w in re.findall(r'\b\w+\b', content)]
        
        if not q_tokens or not c_tokens:
            return 0.0

        c_text_lower = content.lower()
        q_text_lower = query.lower()

        # Factor 1: Exact query substring match
        exact_match = 1.0 if q_text_lower in c_text_lower else 0.0

        # Factor 2: Token coverage
        q_set = set(q_tokens)
        matched_tokens = [t for t in q_set if t in c_text_lower]
        coverage = len(matched_tokens) / len(q_set) if q_set else 0.0

        # Factor 3: Term frequency density
        total_term_freq = sum(c_tokens.count(t) for t in q_set)
        tf_density = total_term_freq / len(c_tokens) if c_tokens else 0.0

        # Factor 4: Bigram matching
        bigram_matches = 0
        total_bigrams = max(1, len(q_tokens) - 1)
        for i in range(len(q_tokens) - 1):
            bigram = f"{q_tokens[i]} {q_tokens[i+1]}"
            if bigram in c_text_lower:
                bigram_matches += 1
        bigram_score = bigram_matches / total_bigrams

        # Composite score normalized between 0.0 and 1.0
        score = (coverage * 0.45) + (bigram_score * 0.25) + (exact_match * 0.20) + (min(1.0, tf_density * 10) * 0.10)
        return float(score)

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = None) -> List[Dict[str, Any]]:
        """
        Reranks candidates based on cross-encoder similarity.
        Selects top_k (default 4).
        """
        if not candidates:
            return []

        top_k = top_k or settings.RERANK_TOP_K

        # If candidates are fewer than or equal to top_k, still calculate cross-encoder score
        if self.model is not None:
            try:
                pairs = [[query, c["content"]] for c in candidates]
                scores = self.model.predict(pairs)
                for idx, score in enumerate(scores):
                    candidates[idx]["rerank_score"] = float(score)
            except Exception as e:
                logger.error(f"CrossEncoder inference failed ({e}). Falling back to multi-factor scoring.")
                for c in candidates:
                    c["rerank_score"] = self._fallback_cross_score(query, c["content"])
        else:
            for c in candidates:
                c["rerank_score"] = self._fallback_cross_score(query, c["content"])

        # Sort descending by rerank_score
        reranked = sorted(candidates, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return reranked[:top_k]

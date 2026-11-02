import hashlib
import math
import numpy as np
from typing import List, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        
        # Check if real OpenAI API key is available
        self.has_openai_key = bool(
            self.api_key and 
            not self.api_key.startswith("sk-placeholder") and 
            not self.api_key.startswith("your-") and
            len(self.api_key.strip()) > 10
        )
        
        if self.has_openai_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI Embedding client initialized with model '{self.model}'.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client ({e}). Falling back to local offline embeddings.")
                self.client = None
                self.has_openai_key = False
        else:
            self.client = None
            logger.info("No valid OpenAI API key detected. Running with deterministic local offline embeddings.")

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generates a deterministic 1536-dimensional normalized vector from text.
        Words share vector components so that lexical and topical overlap
        yields meaningful cosine similarity even in offline test mode.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec.tolist()

        for word in words:
            # Hash word into multiple positions
            for salt in range(4):
                h = int(hashlib.md5(f"{word}_{salt}".encode("utf-8")).hexdigest(), 16)
                idx = h % self.dimension
                val = ((h >> 16) % 1000) / 1000.0 - 0.5
                vec[idx] += val

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single string."""
        embeddings = self.get_embeddings([text])
        return embeddings[0]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of strings."""
        if not texts:
            return []

        # Replace newlines as recommended by OpenAI documentation
        cleaned_texts = [t.replace("\n", " ").strip() for t in texts]

        if self.has_openai_key and self.client:
            try:
                response = self.client.embeddings.create(
                    input=cleaned_texts,
                    model=self.model
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                logger.error(f"OpenAI embedding generation failed: {e}. Falling back to local embeddings for this batch.")
                return [self._generate_mock_embedding(t) for t in cleaned_texts]
        else:
            return [self._generate_mock_embedding(t) for t in cleaned_texts]

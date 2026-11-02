from typing import List, Dict, Any
from app.core.config import settings


class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        # Ensure overlap is strictly less than chunk_size
        if self.chunk_overlap >= self.chunk_size:
            self.chunk_overlap = max(1, self.chunk_size // 10)

    def _split_text_recursively(self, text: str, separators: List[str] = None) -> List[str]:
        """
        Splits text into chunks of maximum length self.chunk_size,
        with overlap self.chunk_overlap, attempting natural break boundaries.
        """
        if separators is None:
            separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]

        if not text:
            return []

        # If text is already under or equal to chunk size, return it as single chunk
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        # Find the best separator that actually splits the text
        chosen_separator = ""
        for sep in separators:
            if sep in text:
                chosen_separator = sep
                break

        # If no separator was found, split directly by character slicing
        if not chosen_separator:
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start += self.chunk_size - self.chunk_overlap
            return chunks

        # Split on the chosen separator
        splits = text.split(chosen_separator)
        final_chunks = []
        current_chunk = ""

        for part in splits:
            if not part:
                continue

            candidate = f"{current_chunk}{chosen_separator}{part}" if current_chunk else part

            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
                    # Overlap handling: take suffix of current chunk
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        current_chunk = f"{overlap_text}{chosen_separator}{part}"
                    else:
                        current_chunk = part
                else:
                    # Single segment is larger than chunk_size, split with subsequent separators
                    remaining_seps = separators[separators.index(chosen_separator) + 1:]
                    sub_chunks = self._split_text_recursively(part, remaining_seps)
                    for sc in sub_chunks:
                        if sc:
                            final_chunks.append(sc)
                    current_chunk = ""

        if current_chunk and current_chunk.strip():
            final_chunks.append(current_chunk.strip())

        return final_chunks

    def chunk_pages(
        self,
        pages_data: List[Dict[str, Any]],
        document_id: str,
        document_name: str,
        department: str = "General",
        category: str = "General"
    ) -> List[Dict[str, Any]]:
        """
        Takes page-by-page extracted data and creates structured chunks preserving metadata.
        Returns list of dicts:
        [{
            "document_id": str,
            "document_name": str,
            "chunk_index": int,
            "page_number": int,
            "content": str,
            "token_count": int,
            "department": str,
            "category": str
        }]
        """
        all_chunks = []
        global_chunk_idx = 0

        for page in pages_data:
            page_num = page["page_number"]
            page_text = page["text"]

            if not page_text or not page_text.strip():
                continue

            split_texts = self._split_text_recursively(page_text)

            for text_chunk in split_texts:
                if not text_chunk or len(text_chunk.strip()) < 10:
                    continue

                # Approximate token count (1 token ~= 4 chars)
                token_count = max(1, len(text_chunk) // 4)

                chunk_dict = {
                    "document_id": document_id,
                    "document_name": document_name,
                    "chunk_index": global_chunk_idx,
                    "page_number": page_num,
                    "content": text_chunk,
                    "token_count": token_count,
                    "department": department,
                    "category": category
                }
                all_chunks.append(chunk_dict)
                global_chunk_idx += 1

        return all_chunks

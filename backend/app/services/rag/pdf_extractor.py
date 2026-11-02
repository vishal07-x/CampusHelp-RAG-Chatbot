import re
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from app.core.logging import logger


class PDFExtractionError(Exception):
    pass


class PDFExtractor:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans raw extracted text:
        - Normalizes unicode characters
        - Removes excessive whitespace/blank lines
        - Fixes hyphenated line breaks
        """
        if not text:
            return ""
        
        # Replace non-breaking spaces and unusual whitespace
        text = text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
        
        # Reconnect hyphenated words split across lines: e.g. "com-\nputer" -> "computer"
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # Collapse multiple spaces on the same line
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Collapse three or more newlines into two
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    @classmethod
    def extract_from_file(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from each page of a PDF document using PyMuPDF.
        Returns a list of dicts: [{"page_number": int, "text": str, "char_count": int}]
        """
        path = Path(file_path)
        if not path.exists():
            raise PDFExtractionError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith(".pdf"):
            raise PDFExtractionError(f"File is not a PDF: {file_path}")

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF {file_path}: {e}")
            raise PDFExtractionError(f"Corrupted or invalid PDF file: {str(e)}")

        if doc.is_encrypted:
            try:
                # Try opening with empty password
                unlocked = doc.authenticate("")
                if not unlocked:
                    raise PDFExtractionError("PDF is password-protected and cannot be read.")
            except Exception as e:
                raise PDFExtractionError(f"Encrypted PDF cannot be read: {str(e)}")

        if len(doc) == 0:
            doc.close()
            raise PDFExtractionError("PDF document contains 0 pages.")

        pages_data = []
        total_extracted_chars = 0

        try:
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_text = page.get_text("text")
                cleaned = cls.clean_text(page_text)
                
                # Page numbers are 1-indexed for student facing citations
                page_number = page_idx + 1
                char_count = len(cleaned)
                total_extracted_chars += char_count

                pages_data.append({
                    "page_number": page_number,
                    "text": cleaned,
                    "char_count": char_count
                })
        except Exception as e:
            logger.error(f"Error while reading pages from {file_path}: {e}")
            raise PDFExtractionError(f"Failed reading pages from PDF: {str(e)}")
        finally:
            doc.close()

        if total_extracted_chars == 0:
            raise PDFExtractionError("No readable text found in PDF. The document may be empty or scanned images without OCR.")

        return pages_data

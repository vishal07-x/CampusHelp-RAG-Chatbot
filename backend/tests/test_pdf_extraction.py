from pathlib import Path
import pytest
from app.services.rag.pdf_extractor import PDFExtractor, PDFExtractionError

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_documents"


def test_pdf_extraction_sample_docs():
    pdf_path = SAMPLE_DIR / "1_Academic_Regulations_and_Attendance_Policy.pdf"
    assert pdf_path.exists(), f"Sample PDF missing: {pdf_path}"

    pages = PDFExtractor.extract_from_file(str(pdf_path))
    assert len(pages) == 2, "Expected 2 pages in academic regulations PDF"
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2
    assert "attendance" in pages[0]["text"].lower()
    assert "75%" in pages[0]["text"]
    assert pages[0]["char_count"] > 100


def test_pdf_extraction_non_existent():
    with pytest.raises(PDFExtractionError):
        PDFExtractor.extract_from_file("non_existent_file.pdf")


def test_clean_text_normalizes_whitespace():
    raw = "Academic    Regulations   \r\n\r\n\r\n\r\nSection  1.1"
    cleaned = PDFExtractor.clean_text(raw)
    assert "  " not in cleaned
    assert "\r" not in cleaned

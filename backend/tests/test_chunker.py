from app.services.rag.chunker import TextChunker


def test_chunker_small_text():
    chunker = TextChunker(chunk_size=500, chunk_overlap=50)
    pages = [
        {"page_number": 1, "text": "This is a short paragraph of college regulation information."}
    ]
    chunks = chunker.chunk_pages(pages, document_id="doc1", document_name="rules.pdf")
    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["document_id"] == "doc1"
    assert chunks[0]["document_name"] == "rules.pdf"
    assert "college regulation" in chunks[0]["content"]


def test_chunker_splits_large_text_with_overlap():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    long_text = "Sentence one is here. " * 20  # ~440 characters
    pages = [{"page_number": 1, "text": long_text}]
    chunks = chunker.chunk_pages(pages, document_id="doc1", document_name="rules.pdf")

    assert len(chunks) > 1
    for c in chunks:
        assert len(c["content"]) <= 120  # Allows slight margin around boundary
        assert c["page_number"] == 1

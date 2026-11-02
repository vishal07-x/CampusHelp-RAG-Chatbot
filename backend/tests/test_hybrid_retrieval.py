from app.services.rag.bm25_retriever import BM25RetrieverService
from app.services.rag.reranker import CrossEncoderReranker
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vector_db import VectorDBService


def test_bm25_indexing_and_search():
    bm25 = BM25RetrieverService()
    sample_chunks = [
        {
            "document_id": "doc1",
            "document_name": "Attendance.pdf",
            "chunk_index": 0,
            "page_number": 1,
            "content": "Minimum attendance requirement is 75 percent for semester exams.",
            "department": "Academics",
            "category": "Policy"
        },
        {
            "document_id": "doc2",
            "document_name": "Fees.pdf",
            "chunk_index": 0,
            "page_number": 1,
            "content": "Tuition fees must be paid before August 15 without late fine.",
            "department": "Finance",
            "category": "Fee"
        }
    ]
    bm25.index_chunks(sample_chunks)

    # Search for attendance
    results = bm25.search("attendance percentage requirement")
    assert len(results) > 0
    assert results[0]["document_id"] == "doc1"

    # Search with department filter
    res_filtered = bm25.search("tuition fees", department_filter="Finance")
    assert len(res_filtered) == 1
    assert res_filtered[0]["document_id"] == "doc2"


def test_reranker_prioritizes_exact_match():
    reranker = CrossEncoderReranker()
    query = "What is the CGPA cutoff for placement?"
    candidates = [
        {
            "content": "The library is open from 8am to 10pm.",
            "score": 0.5
        },
        {
            "content": "The minimum cumulative CGPA cutoff for campus placement is 6.50.",
            "score": 0.6
        }
    ]
    reranked = reranker.rerank(query, candidates, top_k=2)
    assert len(reranked) == 2
    assert "CGPA cutoff for campus placement" in reranked[0]["content"]
    assert reranked[0]["rerank_score"] > reranked[1]["rerank_score"]


def test_vector_db_and_embedding_service():
    emb = EmbeddingService()
    vector = emb.get_embedding("Test attendance query")
    assert len(vector) == 1536
    assert isinstance(vector[0], float)

    vdb = VectorDBService()
    chunks = [{
        "document_id": "test_doc",
        "document_name": "test.pdf",
        "chunk_index": 0,
        "page_number": 1,
        "content": "Testing vector database insertion and cosine similarity.",
        "department": "General",
        "category": "General"
    }]
    point_ids = vdb.upsert_chunks(chunks, [vector])
    assert len(point_ids) == 1

    search_hits = vdb.search(vector, top_k=1)
    assert len(search_hits) >= 1
    assert search_hits[0]["document_id"] == "test_doc"

    # Cleanup
    vdb.delete_document_points("test_doc")

import pytest
from fastapi import HTTPException

from app.services import rag_service, retrieval_service


def test_nonexistent_document_scope_returns_consistent_404(monkeypatch):
    monkeypatch.setattr(retrieval_service, "get_document_metadata", lambda _: None)

    with pytest.raises(HTTPException) as error:
        retrieval_service.validate_document_scope("missing")

    assert error.value.status_code == 404
    assert error.value.detail == "Document not found"


def test_hybrid_retrieval_bulk_loads_keyword_only_chunks_once(monkeypatch):
    monkeypatch.setattr(retrieval_service, "get_document_metadata", lambda _: {"id": "doc"})
    monkeypatch.setattr(retrieval_service, "generate_embedding", lambda _: [0.1])
    monkeypatch.setattr(
        retrieval_service,
        "search_similar_chunks",
        lambda **_: [{
            "score": 0.8, "chunk_id": "semantic", "document_id": "doc", "chunk_index": 0,
            "character_count": 4, "model_name": "model", "text": "same", "page_start": 1, "page_end": 1,
        }],
    )
    monkeypatch.setattr(
        retrieval_service,
        "search_chunks_by_keyword",
        lambda **_: [
            {"id": "semantic", "snippet": "same"},
            {"id": "keyword", "snippet": "only"},
        ],
    )
    loaded_ids = []
    monkeypatch.setattr(
        retrieval_service,
        "get_chunks_by_ids",
        lambda ids: loaded_ids.append(ids) or {
            "keyword": {
                "document_id": "doc", "chunk_index": 1, "character_count": 4,
                "chunk_text": "only", "page_start": 2, "page_end": 2,
            }
        },
    )

    candidates = retrieval_service.retrieve_hybrid_candidates(query="same", document_id="doc")

    assert loaded_ids == [["keyword"]]
    assert {candidate["chunk_id"] for candidate in candidates} == {"semantic", "keyword"}
    assert next(candidate for candidate in candidates if candidate["chunk_id"] == "keyword")["page_start"] == 2


def test_qa_delegates_to_shared_retrieval_pipeline(monkeypatch):
    expected = [{"chunk_id": "chunk"}]
    monkeypatch.setattr(rag_service, "retrieve_hybrid_results", lambda **_: expected)

    assert rag_service.retrieve_context_for_question(question="question") == expected


def test_page_aware_citations_keep_existing_fields():
    citations = rag_service.build_source_citations([{
        "document_id": "doc", "chunk_id": "chunk", "chunk_index": 0, "text": "text",
        "rerank_score": 0.5, "semantic_score": 0.4, "keyword_match": True,
        "page_start": 2, "page_end": 3,
    }])

    assert citations[0]["page_start"] == 2
    assert citations[0]["page_end"] == 3
    assert citations[0]["rerank_score"] == 0.5

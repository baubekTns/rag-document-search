from app.schemas.api import AnswerQuality, Citation, SemanticSearchResponse
from app.services.answer_quality_service import assess_context_quality


def test_quality_schema_is_valid_for_empty_context():
    quality = AnswerQuality.model_validate(assess_context_quality(context_chunks=[]))

    assert quality.is_answerable is False
    assert quality.thresholds.min_top_rerank_score == 0.25


def test_semantic_result_schema_accepts_nullable_payload_fields():
    response = SemanticSearchResponse.model_validate(
        {
            "query": "test",
            "document_id": None,
            "result_count": 1,
            "results": [{
                "score": 0.4,
                "chunk_id": None,
                "document_id": None,
                "chunk_index": None,
                "character_count": None,
                "model_name": None,
                "text": None,
                "page_start": None,
                "page_end": None,
            }],
        }
    )

    assert response.results[0].chunk_id is None


def test_citation_schema_allows_nullable_scores():
    citation = Citation.model_validate(
        {
            "source_number": 1,
            "document_id": "document",
            "chunk_id": "chunk",
            "chunk_index": 0,
            "preview": "Preview",
            "rerank_score": None,
            "semantic_score": None,
            "keyword_match": None,
            "page_start": None,
            "page_end": None,
        }
    )

    assert citation.rerank_score is None

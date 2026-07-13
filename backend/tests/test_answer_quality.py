from app.services.answer_quality_service import assess_context_quality


def test_answer_quality_rejects_empty_context():
    result = assess_context_quality(context_chunks=[])

    assert result["is_answerable"] is False
    assert result["reason"] == "No relevant context was retrieved."


def test_answer_quality_rejects_weak_context():
    context_chunks = [
        {
            "rerank_score": 0.1,
            "semantic_score": 0.1,
            "lexical_score": 0.0,
        }
    ]

    result = assess_context_quality(context_chunks=context_chunks)

    assert result["is_answerable"] is False


def test_answer_quality_accepts_strong_context():
    context_chunks = [
        {
            "rerank_score": 0.6,
            "semantic_score": 0.5,
            "lexical_score": 0.2,
        }
    ]

    result = assess_context_quality(context_chunks=context_chunks)

    assert result["is_answerable"] is True
from app.services.chunk_metadata_service import build_safe_fts_query


def test_build_safe_fts_query_removes_punctuation():
    query = "What is the foreword for?"

    result = build_safe_fts_query(query)

    assert result == "foreword"


def test_build_safe_fts_query_returns_valid_terms():
    query = "How does document search handle uploaded files?"

    result = build_safe_fts_query(query)

    assert "?" not in result
    assert "document" in result
    assert "search" in result
    assert "uploaded" in result
    assert "files" in result
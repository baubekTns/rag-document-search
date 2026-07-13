from app.services.text_chunking_service import chunk_text


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("") == []


def test_chunk_text_splits_text_with_overlap():
    text = "a" * 2500

    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=200)

    assert len(chunks) == 4
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_chunk_text_rejects_invalid_overlap():
    try:
        chunk_text("hello", chunk_size=100, chunk_overlap=100)
    except ValueError as error:
        assert str(error) == "chunk_overlap must be smaller than chunk_size"
    else:
        raise AssertionError("Expected ValueError")
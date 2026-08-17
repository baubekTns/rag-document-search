from app.services.text_chunking_service import chunk_page_texts, chunk_text


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


def test_page_chunks_preserve_page_metadata_and_word_boundaries():
    chunks = chunk_page_texts(
        [{"page_number": 2, "text": "alpha beta gamma delta epsilon"}],
        chunk_size=12,
        chunk_overlap=3,
    )

    assert all(chunk["page_start"] == 2 and chunk["page_end"] == 2 for chunk in chunks)
    assert chunks[0]["text"] == "alpha beta"

from pathlib import Path

import pytest

from app.core.database import apply_schema_migrations, initialize_schema_version, transaction
from app.core.settings import get_settings
from app.services import document_cleanup_service, document_ingestion_service
from app.services.chunk_metadata_service import initialize_chunk_keyword_index, initialize_document_chunks_table
from app.services.document_metadata_service import get_document_metadata, initialize_document_metadata_table
from app.services.embedding_metadata_service import initialize_chunk_embeddings_table


@pytest.fixture(autouse=True)
def isolated_ingestion_storage(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_DATABASE_PATH", str(tmp_path / "documents.db"))
    monkeypatch.setenv("UPLOAD_DIRECTORY", str(tmp_path / "uploads"))
    monkeypatch.setenv("UPLOAD_STAGING_DIRECTORY", str(tmp_path / "uploads" / ".staging"))
    get_settings.cache_clear()
    with transaction() as connection:
        initialize_schema_version(connection)
        initialize_document_metadata_table(connection)
        initialize_document_chunks_table(connection)
        initialize_chunk_keyword_index(connection)
        initialize_chunk_embeddings_table(connection)
        apply_schema_migrations(connection)
    monkeypatch.setattr(document_cleanup_service, "delete_document_vectors", lambda _: None)
    yield tmp_path
    get_settings.cache_clear()


def _extraction(_: Path) -> dict:
    return {
        "pages": 1,
        "characters": 12,
        "text_preview": "Example text",
        "text": "Example text",
        "page_texts": [{"page_number": 1, "text": "Example text"}],
    }


def _configure_success(monkeypatch):
    monkeypatch.setattr(document_ingestion_service, "extract_pdf_text", _extraction)
    monkeypatch.setattr(
        document_ingestion_service,
        "chunk_page_texts",
        lambda *_args, **_kwargs: [{"text": "Example text", "page_start": 1, "page_end": 1}],
    )
    monkeypatch.setattr(document_ingestion_service, "generate_embeddings", lambda _: [[0.1, 0.2]])
    monkeypatch.setattr(document_ingestion_service, "store_chunk_vectors", lambda **_: 1)


def _ingest():
    staged_path = get_settings().upload_staging_directory / "document-1.part"
    staged_path.parent.mkdir(parents=True, exist_ok=True)
    staged_path.write_bytes(b"pdf-content")
    return document_ingestion_service.ingest_document(
        document_id="document-1",
        original_filename="example.pdf",
        stored_filename="document-1_example.pdf",
        content_type="application/pdf",
        staged_path=staged_path,
        file_size=len(b"pdf-content"),
    )


def test_successful_ingestion_promotes_file_and_marks_document_ready(monkeypatch):
    _configure_success(monkeypatch)

    result = _ingest()

    assert result["document"]["processing_status"] == "ready"
    assert get_document_metadata("document-1")["processing_status"] == "ready"
    assert (get_settings().upload_directory / "document-1_example.pdf").is_file()
    assert not (get_settings().upload_staging_directory / "document-1.part").exists()


def test_extraction_failure_removes_staged_state(monkeypatch):
    monkeypatch.setattr(document_ingestion_service, "extract_pdf_text", lambda _: (_ for _ in ()).throw(ValueError("bad PDF")))

    with pytest.raises(ValueError, match="bad PDF"):
        _ingest()

    assert get_document_metadata("document-1") is None
    assert not (get_settings().upload_staging_directory / "document-1.part").exists()


def test_sqlite_persistence_failure_rolls_back_and_cleans_up(monkeypatch):
    _configure_success(monkeypatch)
    monkeypatch.setattr(
        document_ingestion_service,
        "create_document_chunks",
        lambda **_: (_ for _ in ()).throw(RuntimeError("database write failed")),
    )

    with pytest.raises(RuntimeError, match="database write failed"):
        _ingest()

    assert get_document_metadata("document-1") is None
    assert not (get_settings().upload_staging_directory / "document-1.part").exists()


def test_qdrant_upsert_failure_rolls_back_and_requests_vector_cleanup(monkeypatch):
    _configure_success(monkeypatch)
    cleanup_calls = []
    monkeypatch.setattr(
        document_ingestion_service,
        "store_chunk_vectors",
        lambda **_: (_ for _ in ()).throw(RuntimeError("qdrant unavailable")),
    )
    monkeypatch.setattr(document_cleanup_service, "delete_document_vectors", cleanup_calls.append)

    with pytest.raises(RuntimeError, match="qdrant unavailable"):
        _ingest()

    assert cleanup_calls == ["document-1"]
    assert get_document_metadata("document-1") is None


def test_final_file_promotion_failure_cleans_persisted_state(monkeypatch):
    _configure_success(monkeypatch)
    monkeypatch.setattr(
        document_ingestion_service,
        "promote_staged_file",
        lambda *_: (_ for _ in ()).throw(OSError("promotion failed")),
    )

    with pytest.raises(OSError, match="promotion failed"):
        _ingest()

    assert get_document_metadata("document-1") is None
    assert not (get_settings().upload_staging_directory / "document-1.part").exists()


def test_cleanup_is_idempotent(monkeypatch):
    _configure_success(monkeypatch)
    _ingest()
    calls = []
    monkeypatch.setattr(document_cleanup_service, "delete_document_vectors", calls.append)

    first = document_cleanup_service.cleanup_document("document-1")
    second = document_cleanup_service.cleanup_document("document-1")

    assert first.errors == []
    assert second.errors == []
    assert calls == ["document-1", "document-1"]
    assert get_document_metadata("document-1") is None


def test_cleanup_failure_is_reported_and_a_retry_is_safe(monkeypatch):
    _configure_success(monkeypatch)
    _ingest()
    monkeypatch.setattr(
        document_cleanup_service,
        "delete_document_vectors",
        lambda _: (_ for _ in ()).throw(RuntimeError("vector cleanup failed")),
    )

    failed_cleanup = document_cleanup_service.cleanup_document("document-1")
    monkeypatch.setattr(document_cleanup_service, "delete_document_vectors", lambda _: None)
    retried_cleanup = document_cleanup_service.cleanup_document("document-1")

    assert failed_cleanup.errors
    assert retried_cleanup.errors == []
    assert get_document_metadata("document-1") is None

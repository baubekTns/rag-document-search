"""Idempotent removal and inspection helpers for document ingestion state."""

from dataclasses import dataclass, field
import logging
from pathlib import Path

from app.core.database import transaction
from app.core.settings import get_settings
from app.services.document_metadata_service import delete_document_records, get_document_metadata, list_document_metadata
from app.services.vector_store_service import count_document_vectors, delete_document_vectors, get_qdrant_client, QDRANT_COLLECTION_NAME
from app.core.logging import log_error_event


logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    document_id: str
    errors: list[str] = field(default_factory=list)


def cleanup_document(document_id: str, stored_filename: str | None = None) -> CleanupResult:
    """Remove document state from all stores; missing state is treated as already clean."""
    result = CleanupResult(document_id=document_id)
    metadata = get_document_metadata(document_id)
    filename = stored_filename or (metadata or {}).get("stored_filename")

    try:
        delete_document_vectors(document_id)
    except Exception as error:
        log_error_event(logger, "cleanup_failed", document_id=document_id, component="qdrant")
        result.errors.append(str(error))

    try:
        with transaction() as connection:
            delete_document_records(document_id, connection)
    except Exception as error:
        log_error_event(logger, "cleanup_failed", document_id=document_id, component="sqlite")
        result.errors.append(str(error))

    settings = get_settings()
    file_paths = [settings.upload_staging_directory / f"{document_id}.part"]
    if filename:
        file_paths.append(settings.upload_directory / filename)
    for path in file_paths:
        try:
            path.unlink(missing_ok=True)
        except OSError as error:
            log_error_event(logger, "cleanup_failed", document_id=document_id, component="file_storage")
            result.errors.append(str(error))
    return result


def reconcile_document_storage() -> dict[str, list[str]]:
    """Report obvious cross-store inconsistencies without changing any data."""
    documents = list_document_metadata()
    known_document_ids = {document["id"] for document in documents}
    settings = get_settings()
    report = {
        "processing_documents": [],
        "missing_files": [],
        "missing_vectors": [],
        "orphaned_vector_documents": [],
    }
    for document in documents:
        document_id = document["id"]
        if document["processing_status"] == "processing":
            report["processing_documents"].append(document_id)
        if not (settings.upload_directory / document["stored_filename"]).is_file():
            report["missing_files"].append(document_id)
        if document["processing_status"] == "ready" and count_document_vectors(document_id) == 0:
            report["missing_vectors"].append(document_id)

    client = get_qdrant_client()
    offset = None
    vector_document_ids: set[str] = set()
    while True:
        points, offset = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            scroll_filter=None,
            with_payload=["document_id"],
            with_vectors=False,
            offset=offset,
            limit=100,
        )
        vector_document_ids.update(
            point.payload["document_id"]
            for point in points
            if point.payload and point.payload.get("document_id")
        )
        if offset is None:
            break
    report["orphaned_vector_documents"] = sorted(vector_document_ids - known_document_ids)
    return report

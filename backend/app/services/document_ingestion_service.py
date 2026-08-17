"""Staged, recoverable document ingestion orchestration."""

import logging
from pathlib import Path

from app.core.database import transaction
from app.core.settings import get_settings
from app.services.chunk_metadata_service import create_document_chunks
from app.services.document_cleanup_service import cleanup_document
from app.services.document_metadata_service import create_document_metadata, update_document_processing_status
from app.services.embedding_metadata_service import create_chunk_embeddings
from app.services.embedding_service import EMBEDDING_MODEL_NAME, generate_embeddings
from app.services.pdf_service import extract_pdf_text
from app.services.text_chunking_service import chunk_text
from app.services.vector_store_service import QDRANT_COLLECTION_NAME, store_chunk_vectors


logger = logging.getLogger(__name__)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def promote_staged_file(staged_path: Path, final_path: Path) -> None:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    staged_path.replace(final_path)


def ingest_document(
    *,
    document_id: str,
    original_filename: str,
    stored_filename: str,
    content_type: str,
    contents: bytes,
) -> dict:
    """Ingest a validated upload and leave no ready state after a failure."""
    settings = get_settings()
    settings.upload_directory.mkdir(parents=True, exist_ok=True)
    settings.upload_staging_directory.mkdir(parents=True, exist_ok=True)
    staged_path = settings.upload_staging_directory / f"{document_id}.part"
    final_path = settings.upload_directory / stored_filename
    staged_path.write_bytes(contents)

    try:
        extraction = extract_pdf_text(staged_path)
        chunks = chunk_text(extraction["text"], chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        embeddings = generate_embeddings(chunks)

        # Qdrant is intentionally inside the SQLite transaction. If either store fails,
        # the transaction rolls back and the compensating cleanup removes vector state.
        with transaction() as connection:
            document_metadata = create_document_metadata(
                document_id=document_id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                content_type=content_type,
                file_size=len(contents),
                page_count=extraction["pages"],
                character_count=extraction["characters"],
                processing_status="processing",
                connection=connection,
            )
            chunk_records = create_document_chunks(
                document_id=document_id, chunks=chunks, connection=connection
            )
            embedding_records = create_chunk_embeddings(
                document_id=document_id,
                chunk_records=chunk_records,
                embeddings=embeddings,
                model_name=EMBEDDING_MODEL_NAME,
                connection=connection,
            )
            vector_count = store_chunk_vectors(
                document_id=document_id,
                chunk_records=chunk_records,
                embeddings=embeddings,
                model_name=EMBEDDING_MODEL_NAME,
            )

        promote_staged_file(staged_path, final_path)
        update_document_processing_status(document_id, "ready")
        document_metadata["processing_status"] = "ready"
        return {
            "message": "PDF uploaded, text extracted, chunked, indexed, embedded, and stored in vector database successfully",
            "document": document_metadata,
            "chunking": {"chunk_count": len(chunk_records), "chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP},
            "embeddings": {
                "embedding_count": len(embedding_records),
                "model_name": EMBEDDING_MODEL_NAME,
                "embedding_dimension": embedding_records[0]["embedding_dimension"] if embedding_records else 0,
            },
            "vector_storage": {"stored_vector_count": vector_count, "collection_name": QDRANT_COLLECTION_NAME},
            "text_preview": extraction["text_preview"],
        }
    except Exception:
        cleanup_result = cleanup_document(document_id, stored_filename)
        if cleanup_result.errors:
            logger.error("Ingestion compensation incomplete for document_id=%s", document_id)
        raise

import sqlite3
from datetime import datetime, timezone
from typing import Any
from app.core.database import get_connection, transaction


def initialize_document_metadata_table(connection: sqlite3.Connection | None = None) -> None:
    if connection is None:
        with transaction() as transaction_connection:
            initialize_document_metadata_table(transaction_connection)
        return
    connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                page_count INTEGER NOT NULL,
                character_count INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL,
                processing_status TEXT NOT NULL DEFAULT 'ready'
                    CHECK (processing_status IN ('processing', 'ready', 'failed'))
            )
            """
    )


def create_document_metadata(
    *,
    document_id: str,
    original_filename: str,
    stored_filename: str,
    content_type: str,
    file_size: int,
    page_count: int,
    character_count: int,
    processing_status: str = "ready",
    connection: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    uploaded_at = datetime.now(timezone.utc).isoformat()

    if connection is None:
        with transaction() as transaction_connection:
            return create_document_metadata(
                document_id=document_id, original_filename=original_filename,
                stored_filename=stored_filename, content_type=content_type, file_size=file_size,
                page_count=page_count, character_count=character_count,
                processing_status=processing_status, connection=transaction_connection,
            )
    connection.execute(
            """
            INSERT INTO documents (
                id,
                original_filename,
                stored_filename,
                content_type,
                file_size,
                page_count,
                character_count,
                uploaded_at,
                processing_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                original_filename,
                stored_filename,
                content_type,
                file_size,
                page_count,
                character_count,
                uploaded_at,
                processing_status,
            ),
    )

    return {
        "id": document_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "content_type": content_type,
        "file_size": file_size,
        "page_count": page_count,
        "character_count": character_count,
        "uploaded_at": uploaded_at,
        "processing_status": processing_status,
    }


def list_document_metadata() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                original_filename,
                stored_filename,
                content_type,
                file_size,
                page_count,
                character_count,
                uploaded_at,
                processing_status
            FROM documents
            ORDER BY uploaded_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_document_metadata(document_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                original_filename,
                stored_filename,
                content_type,
                file_size,
                page_count,
                character_count,
                uploaded_at,
                processing_status
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def update_document_processing_status(document_id: str, status: str) -> None:
    with transaction() as connection:
        connection.execute(
            "UPDATE documents SET processing_status = ? WHERE id = ?",
            (status, document_id),
        )


def delete_document_records(document_id: str, connection: sqlite3.Connection | None = None) -> None:
    if connection is None:
        with transaction() as transaction_connection:
            delete_document_records(document_id, transaction_connection)
        return
    connection.execute("DELETE FROM chunk_embeddings WHERE document_id = ?", (document_id,))
    connection.execute("DELETE FROM document_chunks_fts WHERE document_id = ?", (document_id,))
    connection.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
    connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))

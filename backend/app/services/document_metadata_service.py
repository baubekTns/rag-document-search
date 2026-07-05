import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "documents.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_document_metadata_table() -> None:
    with get_connection() as connection:
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
                uploaded_at TEXT NOT NULL
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
) -> dict[str, Any]:
    uploaded_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
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
                uploaded_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
                uploaded_at
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
                uploaded_at
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)
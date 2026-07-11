import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
import re


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "documents.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_document_chunks_table() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                character_count INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
            """
        )


def create_document_chunks(
    *,
    document_id: str,
    chunks: list[str],
) -> list[dict[str, Any]]:
    created_at = datetime.now(timezone.utc).isoformat()

    chunk_records = [
        {
            "id": str(uuid4()),
            "document_id": document_id,
            "chunk_index": index,
            "chunk_text": chunk,
            "character_count": len(chunk),
            "created_at": created_at,
        }
        for index, chunk in enumerate(chunks)
    ]

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO document_chunks (
                id,
                document_id,
                chunk_index,
                chunk_text,
                character_count,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    record["id"],
                    record["document_id"],
                    record["chunk_index"],
                    record["chunk_text"],
                    record["character_count"],
                    record["created_at"],
                )
                for record in chunk_records
            ],
        )

        connection.executemany(
            """
            INSERT INTO document_chunks_fts (
                chunk_id,
                document_id,
                chunk_text
            )
            VALUES (?, ?, ?)
            """,
            [
                (
                    record["id"],
                    record["document_id"],
                    record["chunk_text"],
                )
                for record in chunk_records
            ],
        )

    return chunk_records

def list_chunk_previews_for_document(
    document_id: str,
    preview_length: int = 200,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                chunk_text,
                character_count,
                created_at
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (document_id,),
        ).fetchall()

    previews = []

    for row in rows:
        chunk = dict(row)
        chunk_text = chunk.pop("chunk_text")

        previews.append(
            {
                **chunk,
                "preview": chunk_text[:preview_length],
            }
        )

    return previews


def get_chunk_by_id(document_id: str, chunk_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                chunk_text,
                character_count,
                created_at
            FROM document_chunks
            WHERE document_id = ? AND id = ?
            """,
            (document_id, chunk_id),
        ).fetchone()

    if row is None:
        return None

    return dict(row)

def initialize_chunk_keyword_index() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts
            USING fts5(
                chunk_id UNINDEXED,
                document_id UNINDEXED,
                chunk_text
            )
            """
        )

def build_safe_fts_query(query: str) -> str:
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "what",
        "when",
        "where",
        "why",
        "how",
        "who",
        "does",
        "this",
        "that",
        "from",
        "into",
        "before",
        "after",
        "about",
    }

    tokens = re.findall(r"[a-zA-Z0-9]+", query.lower())

    tokens = [
        token
        for token in tokens
        if len(token) > 2 and token not in stop_words
    ]

    return " OR ".join(tokens)

def search_chunks_by_keyword(
    *,
    query: str,
    document_id: str | None = None,
    limit: int = 10,
    preview_length: int = 250,
) -> list[dict[str, Any]]:
    cleaned_query = build_safe_fts_query(query)

    if not cleaned_query:
        return []

    sql = """
        SELECT
            c.id,
            c.document_id,
            c.chunk_index,
            c.character_count,
            c.created_at,
            snippet(document_chunks_fts, 2, '<mark>', '</mark>', '...', 20) AS snippet,
            substr(c.chunk_text, 1, ?) AS preview
        FROM document_chunks_fts
        JOIN document_chunks c
            ON c.id = document_chunks_fts.chunk_id
        WHERE document_chunks_fts MATCH ?
    """

    params: list[Any] = [preview_length, cleaned_query]

    if document_id is not None:
        sql += " AND c.document_id = ?"
        params.append(document_id)

    sql += """
        ORDER BY bm25(document_chunks_fts)
        LIMIT ?
    """
    params.append(limit)

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()

    return [dict(row) for row in rows]
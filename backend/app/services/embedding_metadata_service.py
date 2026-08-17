import json
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


from app.core.database import get_connection, transaction


def initialize_chunk_embeddings_table(connection: sqlite3.Connection | None = None) -> None:
    if connection is None:
        with transaction() as transaction_connection:
            initialize_chunk_embeddings_table(transaction_connection)
        return
    connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunk_embeddings (
                id TEXT PRIMARY KEY,
                chunk_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                embedding_dimension INTEGER NOT NULL,
                embedding_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (chunk_id) REFERENCES document_chunks(id),
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE (chunk_id, model_name)
            )
            """
    )


def create_chunk_embeddings(
    *,
    document_id: str,
    chunk_records: list[dict[str, Any]],
    embeddings: list[list[float]],
    model_name: str,
    connection: sqlite3.Connection | None = None,
) -> list[dict[str, Any]]:
    if len(chunk_records) != len(embeddings):
        raise ValueError("chunk_records and embeddings must have the same length")

    created_at = datetime.now(timezone.utc).isoformat()

    embedding_records = []

    for chunk_record, embedding in zip(chunk_records, embeddings):
        embedding_records.append(
            {
                "id": str(uuid4()),
                "chunk_id": chunk_record["id"],
                "document_id": document_id,
                "model_name": model_name,
                "embedding_dimension": len(embedding),
                "embedding_json": json.dumps(embedding),
                "created_at": created_at,
            }
        )

    if connection is None:
        with transaction() as transaction_connection:
            return create_chunk_embeddings(
                document_id=document_id, chunk_records=chunk_records, embeddings=embeddings,
                model_name=model_name, connection=transaction_connection,
            )
    connection.executemany(
            """
            INSERT INTO chunk_embeddings (
                id,
                chunk_id,
                document_id,
                model_name,
                embedding_dimension,
                embedding_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    record["id"],
                    record["chunk_id"],
                    record["document_id"],
                    record["model_name"],
                    record["embedding_dimension"],
                    record["embedding_json"],
                    record["created_at"],
                )
                for record in embedding_records
            ],
    )

    return embedding_records


def list_embedding_metadata_for_document(document_id: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                chunk_id,
                document_id,
                model_name,
                embedding_dimension,
                created_at
            FROM chunk_embeddings
            WHERE document_id = ?
            ORDER BY created_at ASC
            """,
            (document_id,),
        ).fetchall()

    return [dict(row) for row in rows]

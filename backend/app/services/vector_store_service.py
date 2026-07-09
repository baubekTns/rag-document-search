import os
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME",
    "document_chunks",
)
VECTOR_SIZE = 384


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)


def count_vectors() -> int:
    client = get_qdrant_client()

    collection_info = client.get_collection(QDRANT_COLLECTION_NAME)

    return collection_info.points_count or 0


def initialize_vector_collection() -> None:
    client = get_qdrant_client()

    if client.collection_exists(QDRANT_COLLECTION_NAME):
        return

    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def store_chunk_vectors(
    *,
    document_id: str,
    chunk_records: list[dict[str, Any]],
    embeddings: list[list[float]],
    model_name: str,
) -> int:
    if len(chunk_records) != len(embeddings):
        raise ValueError("chunk_records and embeddings must have the same length")

    client = get_qdrant_client()

    points = []

    for chunk_record, embedding in zip(chunk_records, embeddings):
        points.append(
            PointStruct(
                id=chunk_record["id"],
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_id": chunk_record["id"],
                    "chunk_index": chunk_record["chunk_index"],
                    "character_count": chunk_record["character_count"],
                    "model_name": model_name,
                    "text": chunk_record["chunk_text"],
                },
            )
        )

    if not points:
        return 0

    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points,
    )

    return len(points)
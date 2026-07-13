import os
from typing import Any
from app.core.exceptions import VectorStoreError
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
    try:
        client = get_qdrant_client()
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)

        return collection_info.points_count or 0

    except Exception as error:
        raise VectorStoreError(
            f"Failed to read Qdrant collection status: {error}"
        )


def initialize_vector_collection() -> None:
    client = get_qdrant_client()

    try:
        if client.collection_exists(QDRANT_COLLECTION_NAME):
            return

        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    except Exception as error:
        raise VectorStoreError(
            f"Failed to initialize Qdrant collection: {error}"
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

    try:
        client = get_qdrant_client()
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points,
        )

        return len(points)

    except Exception as error:
        raise VectorStoreError(
            f"Failed to store vectors in Qdrant: {error}"
        )


def search_similar_chunks(
    *,
    query_embedding: list[float],
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict[str, Any]]:
    client = get_qdrant_client()

    query_filter = None

    if document_id is not None:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        query_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        )

    try:
        search_response = client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_embedding,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

    except Exception as error:
        raise VectorStoreError(
            f"Failed to search vectors in Qdrant: {error}"
        )

    results = []

    for point in search_response.points:
        payload = point.payload or {}

        results.append(
            {
                "score": point.score,
                "chunk_id": payload.get("chunk_id"),
                "document_id": payload.get("document_id"),
                "chunk_index": payload.get("chunk_index"),
                "character_count": payload.get("character_count"),
                "model_name": payload.get("model_name"),
                "text": payload.get("text"),
            }
        )

    return results

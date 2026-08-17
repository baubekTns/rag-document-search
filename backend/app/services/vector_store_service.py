from functools import lru_cache
from typing import Any
from app.core.exceptions import VectorStoreError
from app.core.settings import get_settings
from app.services.embedding_service import get_embedding_dimension
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams


QDRANT_URL = get_settings().qdrant_url
QDRANT_COLLECTION_NAME = get_settings().qdrant_collection_name

@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL, timeout=get_settings().qdrant_timeout_seconds)


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
    vector_size = get_embedding_dimension()

    try:
        if client.collection_exists(QDRANT_COLLECTION_NAME):
            collection = client.get_collection(QDRANT_COLLECTION_NAME)
            vectors = collection.config.params.vectors
            if isinstance(vectors, dict):
                raise VectorStoreError("Qdrant collection uses named vectors, but this application uses one unnamed vector")
            if vectors.size != vector_size or vectors.distance != Distance.COSINE:
                raise VectorStoreError(
                    "Qdrant collection configuration is incompatible: "
                    f"expected size={vector_size}, distance=Cosine; "
                    f"found size={vectors.size}, distance={vectors.distance}"
                )
            return

        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
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
                    "page_start": chunk_record.get("page_start"),
                    "page_end": chunk_record.get("page_end"),
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


def document_vector_filter(document_id: str) -> Filter:
    return Filter(
        must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
    )


def delete_document_vectors(document_id: str) -> None:
    """Idempotently remove every vector belonging to a document."""
    try:
        get_qdrant_client().delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=document_vector_filter(document_id),
        )
    except Exception as error:
        raise VectorStoreError(f"Failed to delete document vectors: {error}")


def count_document_vectors(document_id: str) -> int:
    try:
        result = get_qdrant_client().count(
            collection_name=QDRANT_COLLECTION_NAME,
            count_filter=document_vector_filter(document_id),
            exact=True,
        )
        return result.count
    except Exception as error:
        raise VectorStoreError(f"Failed to count document vectors: {error}")


def search_similar_chunks(
    *,
    query_embedding: list[float],
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict[str, Any]]:
    client = get_qdrant_client()

    query_filter = None

    if document_id is not None:
        query_filter = document_vector_filter(document_id)

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
                "page_start": payload.get("page_start"),
                "page_end": payload.get("page_end"),
            }
        )

    return results

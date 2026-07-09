from fastapi import APIRouter, Query

from app.services.chunk_metadata_service import search_chunks_by_keyword
from app.services.embedding_service import generate_embedding
from app.services.vector_store_service import search_similar_chunks

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/keyword")
def keyword_search(
    q: str = Query(..., min_length=1),
    document_id: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
):
    results = search_chunks_by_keyword(
        query=q,
        document_id=document_id,
        limit=limit,
    )

    return {
        "query": q,
        "document_id": document_id,
        "result_count": len(results),
        "results": results,
    }

@router.get("/semantic")
def semantic_search(
    q: str = Query(..., min_length=1),
    document_id: str | None = None,
    limit: int = Query(default=5, ge=1, le=20),
):
    query_embedding = generate_embedding(q)

    results = search_similar_chunks(
        query_embedding=query_embedding,
        document_id=document_id,
        limit=limit,
    )

    return {
        "query": q,
        "document_id": document_id,
        "result_count": len(results),
        "results": results,
    }
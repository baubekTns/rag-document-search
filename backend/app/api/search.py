from fastapi import APIRouter, Query

from app.services.chunk_metadata_service import search_chunks_by_keyword

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
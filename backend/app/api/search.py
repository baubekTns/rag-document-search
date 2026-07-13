from fastapi import APIRouter, Query

from app.services.chunk_metadata_service import (
    get_chunk_by_id,
    search_chunks_by_keyword,
)
from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_chunks
from app.services.vector_store_service import search_similar_chunks
import logging

logger = logging.getLogger(__name__)
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

    logger.info(
        "Keyword search completed: query=%s document_id=%s result_count=%s",
        q,
        document_id,
        len(results),
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

    logger.info(
        "Semantic search completed: query=%s document_id=%s result_count=%s",
        q,
        document_id,
        len(results),
    )

    return {
        "query": q,
        "document_id": document_id,
        "result_count": len(results),
        "results": results,
    }


@router.get("/reranked")
def reranked_search(
    q: str = Query(..., min_length=1),
    document_id: str | None = None,
    limit: int = Query(default=5, ge=1, le=20),
    candidate_limit: int = Query(default=20, ge=5, le=50),
):
    query_embedding = generate_embedding(q)

    semantic_results = search_similar_chunks(
        query_embedding=query_embedding,
        document_id=document_id,
        limit=candidate_limit,
    )

    keyword_results = search_chunks_by_keyword(
        query=q,
        document_id=document_id,
        limit=candidate_limit,
    )

    candidates_by_chunk_id = {}

    for result in semantic_results:
        chunk_id = result["chunk_id"]

        if chunk_id is None:
            continue

        candidates_by_chunk_id[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": result["document_id"],
            "chunk_index": result["chunk_index"],
            "character_count": result["character_count"],
            "model_name": result["model_name"],
            "text": result["text"],
            "semantic_score": result["score"],
            "keyword_match": False,
        }

    for result in keyword_results:
        chunk_id = result["id"]
        result_document_id = result["document_id"]

        if chunk_id in candidates_by_chunk_id:
            candidates_by_chunk_id[chunk_id]["keyword_match"] = True
            candidates_by_chunk_id[chunk_id]["keyword_snippet"] = result.get("snippet")
            continue

        chunk = get_chunk_by_id(result_document_id, chunk_id)

        if chunk is None:
            continue

        candidates_by_chunk_id[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": result_document_id,
            "chunk_index": result["chunk_index"],
            "character_count": result["character_count"],
            "model_name": None,
            "text": chunk["chunk_text"],
            "semantic_score": 0.0,
            "keyword_match": True,
            "keyword_snippet": result.get("snippet"),
        }

    candidates = list(candidates_by_chunk_id.values())

    reranked_results = rerank_chunks(
        query=q,
        candidates=candidates,
        limit=limit,
    )

    logger.info(
        "Reranked search completed: query=%s document_id=%s candidate_count=%s result_count=%s",
        q,
        document_id,
        len(candidates),
        len(reranked_results),
    )

    return {
        "query": q,
        "document_id": document_id,
        "candidate_count": len(candidates),
        "result_count": len(reranked_results),
        "results": reranked_results,
    }
from fastapi import APIRouter, Depends

from app.services.chunk_metadata_service import (
    get_chunk_by_id,
    search_chunks_by_keyword,
)
from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_chunks
from app.services.vector_store_service import search_similar_chunks
from app.schemas.api import (
    KeywordSearchQuery, KeywordSearchResponse, RerankedSearchQuery,
    RerankedSearchResponse, SemanticSearchQuery, SemanticSearchResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/keyword", response_model=KeywordSearchResponse)
def keyword_search(query: KeywordSearchQuery = Depends()):
    results = search_chunks_by_keyword(
        query=query.q,
        document_id=query.document_id,
        limit=query.limit,
    )

    logger.info(
        "Keyword search completed: query=%s document_id=%s result_count=%s",
        query.q,
        query.document_id,
        len(results),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "result_count": len(results),
        "results": results,
    }


@router.get("/semantic", response_model=SemanticSearchResponse)
def semantic_search(query: SemanticSearchQuery = Depends()):
    query_embedding = generate_embedding(query.q)

    results = search_similar_chunks(
        query_embedding=query_embedding,
        document_id=query.document_id,
        limit=query.limit,
    )

    logger.info(
        "Semantic search completed: query=%s document_id=%s result_count=%s",
        query.q,
        query.document_id,
        len(results),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "result_count": len(results),
        "results": results,
    }


@router.get("/reranked", response_model=RerankedSearchResponse)
def reranked_search(query: RerankedSearchQuery = Depends()):
    query_embedding = generate_embedding(query.q)

    semantic_results = search_similar_chunks(
        query_embedding=query_embedding,
        document_id=query.document_id,
        limit=query.candidate_limit,
    )

    keyword_results = search_chunks_by_keyword(
        query=query.q,
        document_id=query.document_id,
        limit=query.candidate_limit,
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
        query=query.q,
        candidates=candidates,
        limit=query.limit,
    )

    logger.info(
        "Reranked search completed: query=%s document_id=%s candidate_count=%s result_count=%s",
        query.q,
        query.document_id,
        len(candidates),
        len(reranked_results),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "candidate_count": len(candidates),
        "result_count": len(reranked_results),
        "results": reranked_results,
    }

from fastapi import APIRouter, Depends

from app.services.chunk_metadata_service import search_chunks_by_keyword
from app.services.embedding_service import generate_embedding
from app.services.vector_store_service import search_similar_chunks
from app.services.retrieval_service import retrieve_hybrid, validate_document_scope
from app.schemas.api import (
    KeywordSearchQuery, KeywordSearchResponse, RerankedSearchQuery,
    RerankedSearchResponse, SemanticSearchQuery, SemanticSearchResponse,
)
import logging
from time import perf_counter
from app.core.logging import log_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/keyword", response_model=KeywordSearchResponse)
def keyword_search(query: KeywordSearchQuery = Depends()):
    started_at = perf_counter()
    validate_document_scope(query.document_id)
    results = search_chunks_by_keyword(
        query=query.q,
        document_id=query.document_id,
        limit=query.limit,
    )

    log_event(
        logger, "keyword_search_completed", document_id=query.document_id,
        result_count=len(results), duration_ms=round((perf_counter() - started_at) * 1000),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "result_count": len(results),
        "results": results,
    }


@router.get("/semantic", response_model=SemanticSearchResponse)
def semantic_search(query: SemanticSearchQuery = Depends()):
    started_at = perf_counter()
    validate_document_scope(query.document_id)
    query_embedding = generate_embedding(query.q)

    results = search_similar_chunks(
        query_embedding=query_embedding,
        document_id=query.document_id,
        limit=query.limit,
    )

    log_event(
        logger, "semantic_search_completed", document_id=query.document_id,
        result_count=len(results), duration_ms=round((perf_counter() - started_at) * 1000),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "result_count": len(results),
        "results": results,
    }


@router.get("/reranked", response_model=RerankedSearchResponse)
def reranked_search(query: RerankedSearchQuery = Depends()):
    started_at = perf_counter()
    retrieval = retrieve_hybrid(
        query=query.q, document_id=query.document_id, limit=query.limit, candidate_limit=query.candidate_limit
    )
    reranked_results = retrieval.results

    log_event(
        logger, "reranked_search_completed", document_id=query.document_id,
        candidate_count=len(retrieval.candidates), result_count=len(reranked_results),
        duration_ms=round((perf_counter() - started_at) * 1000),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "candidate_count": len(retrieval.candidates),
        "result_count": len(reranked_results),
        "results": reranked_results,
    }

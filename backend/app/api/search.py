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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/keyword", response_model=KeywordSearchResponse)
def keyword_search(query: KeywordSearchQuery = Depends()):
    validate_document_scope(query.document_id)
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
    validate_document_scope(query.document_id)
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
    retrieval = retrieve_hybrid(
        query=query.q, document_id=query.document_id, limit=query.limit, candidate_limit=query.candidate_limit
    )
    reranked_results = retrieval.results

    logger.info(
        "Reranked search completed: query=%s document_id=%s candidate_count=%s result_count=%s",
        query.q,
        query.document_id,
        len(retrieval.candidates),
        len(reranked_results),
    )

    return {
        "query": query.q,
        "document_id": query.document_id,
        "candidate_count": len(retrieval.candidates),
        "result_count": len(reranked_results),
        "results": reranked_results,
    }

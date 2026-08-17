"""The shared hybrid retrieval pipeline used by search and question answering."""

from dataclasses import dataclass

from fastapi import HTTPException

from app.services.chunk_metadata_service import get_chunks_by_ids, search_chunks_by_keyword
from app.services.document_metadata_service import get_document_metadata
from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_chunks
from app.services.vector_store_service import search_similar_chunks


@dataclass
class HybridRetrieval:
    candidates: list[dict]
    results: list[dict]


def validate_document_scope(document_id: str | None) -> None:
    if document_id is not None and get_document_metadata(document_id) is None:
        raise HTTPException(status_code=404, detail="Document not found")


def retrieve_hybrid_candidates(
    *,
    query: str,
    document_id: str | None = None,
    candidate_limit: int = 20,
) -> list[dict]:
    validate_document_scope(document_id)
    semantic_results = search_similar_chunks(
        query_embedding=generate_embedding(query), document_id=document_id, limit=candidate_limit
    )
    keyword_results = search_chunks_by_keyword(
        query=query, document_id=document_id, limit=candidate_limit
    )
    candidates_by_chunk_id: dict[str, dict] = {}
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
            "page_start": result.get("page_start"),
            "page_end": result.get("page_end"),
            "semantic_score": result["score"],
            "keyword_match": False,
        }

    keyword_only_ids = [result["id"] for result in keyword_results if result["id"] not in candidates_by_chunk_id]
    keyword_only_chunks = get_chunks_by_ids(keyword_only_ids)
    for result in keyword_results:
        chunk_id = result["id"]
        if chunk_id in candidates_by_chunk_id:
            candidates_by_chunk_id[chunk_id]["keyword_match"] = True
            candidates_by_chunk_id[chunk_id]["keyword_snippet"] = result.get("snippet")
            continue
        chunk = keyword_only_chunks.get(chunk_id)
        if chunk is None:
            continue
        candidates_by_chunk_id[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": chunk["document_id"],
            "chunk_index": chunk["chunk_index"],
            "character_count": chunk["character_count"],
            "model_name": None,
            "text": chunk["chunk_text"],
            "page_start": chunk.get("page_start"),
            "page_end": chunk.get("page_end"),
            "semantic_score": 0.0,
            "keyword_match": True,
            "keyword_snippet": result.get("snippet"),
        }
    return list(candidates_by_chunk_id.values())


def retrieve_hybrid(
    *,
    query: str,
    document_id: str | None = None,
    limit: int = 5,
    candidate_limit: int = 20,
) -> HybridRetrieval:
    candidates = retrieve_hybrid_candidates(
        query=query, document_id=document_id, candidate_limit=candidate_limit
    )
    return HybridRetrieval(
        candidates=candidates,
        results=rerank_chunks(
            query=query,
            candidates=candidates,
            limit=limit,
        ),
    )


def retrieve_hybrid_results(**kwargs) -> list[dict]:
    return retrieve_hybrid(**kwargs).results

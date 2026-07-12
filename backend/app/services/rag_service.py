from typing import Any

from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_chunks
from app.services.vector_store_service import search_similar_chunks
from app.services.chunk_metadata_service import (
    get_chunk_by_id,
    search_chunks_by_keyword,
)
from app.services.llm_service import generate_answer_with_ollama
from app.services.prompt_service import build_rag_prompt


DEFAULT_CANDIDATE_LIMIT = 20
DEFAULT_CONTEXT_LIMIT = 5


def retrieve_context_for_question(
    *,
    question: str,
    document_id: str | None = None,
    context_limit: int = DEFAULT_CONTEXT_LIMIT,
    candidate_limit: int = DEFAULT_CANDIDATE_LIMIT,
) -> list[dict[str, Any]]:
    query_embedding = generate_embedding(question)

    semantic_results = search_similar_chunks(
        query_embedding=query_embedding,
        document_id=document_id,
        limit=candidate_limit,
    )

    keyword_results = search_chunks_by_keyword(
        query=question,
        document_id=document_id,
        limit=candidate_limit,
    )

    candidates_by_chunk_id: dict[str, dict[str, Any]] = {}

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

    return rerank_chunks(
        query=question,
        candidates=candidates,
        limit=context_limit,
    )


def build_context_text(context_chunks: list[dict[str, Any]]) -> str:
    context_sections = []

    for index, chunk in enumerate(context_chunks, start=1):
        context_sections.append(
            f"[Source {index} | document_id={chunk['document_id']} | "
            f"chunk_id={chunk['chunk_id']} | chunk_index={chunk['chunk_index']}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context_sections)


def create_retrieval_preview_answer(
    *,
    question: str,
    context_chunks: list[dict[str, Any]],
) -> str:
    if not context_chunks:
        return (
            "I could not find relevant context in the uploaded documents for this question."
        )

    return (
        "Relevant context was retrieved successfully. "
        "LLM answer generation has not been added yet, so this endpoint currently "
        "returns the retrieved sources that would be used to answer the question."
    )

def generate_rag_answer(
    *,
    question: str,
    context_chunks: list[dict[str, Any]],
) -> str:
    if not context_chunks:
        return "I could not find relevant context in the uploaded documents."

    prompt = build_rag_prompt(
        question=question,
        context_chunks=context_chunks,
    )

    return generate_answer_with_ollama(prompt)

def build_source_citations(context_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    citations = []

    for index, chunk in enumerate(context_chunks, start=1):
        text = chunk.get("text") or ""

        citations.append(
            {
                "source_number": index,
                "document_id": chunk["document_id"],
                "chunk_id": chunk["chunk_id"],
                "chunk_index": chunk["chunk_index"],
                "preview": text[:300],
                "rerank_score": chunk.get("rerank_score"),
                "semantic_score": chunk.get("semantic_score"),
                "keyword_match": chunk.get("keyword_match"),
            }
        )

    return citations
from typing import Any

from app.services.retrieval_service import retrieve_hybrid_results
from app.services.llm_service import generate_answer_with_ollama
from app.services.prompt_service import build_rag_prompt, validate_citation_markers
from app.core.logging import log_event
import logging
from app.services.answer_quality_service import assess_context_quality


DEFAULT_CANDIDATE_LIMIT = 20
DEFAULT_CONTEXT_LIMIT = 5
logger = logging.getLogger(__name__)


def retrieve_context_for_question(
    *,
    question: str,
    document_id: str | None = None,
    context_limit: int = DEFAULT_CONTEXT_LIMIT,
    candidate_limit: int = DEFAULT_CANDIDATE_LIMIT,
) -> list[dict[str, Any]]:
    return retrieve_hybrid_results(
        query=question,
        document_id=document_id,
        limit=context_limit,
        candidate_limit=candidate_limit,
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

    answer = generate_answer_with_ollama(prompt)
    if not validate_citation_markers(answer, len(context_chunks)):
        log_event(logger, "citation_integrity_failed", source_count=len(context_chunks))
        return "I could not find this in the uploaded documents."
    return answer

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
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
            }
        )

    return citations

def generate_quality_checked_rag_answer(
    *,
    question: str,
    context_chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    quality = assess_context_quality(context_chunks=context_chunks)

    if not quality["is_answerable"]:
        return {
            "answer": "I could not find this in the uploaded documents.",
            "quality": quality,
        }

    answer = generate_rag_answer(
        question=question,
        context_chunks=context_chunks,
    )

    return {
        "answer": answer,
        "quality": quality,
    }

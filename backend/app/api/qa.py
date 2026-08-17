from fastapi import APIRouter, Depends
import logging
from time import perf_counter
from app.services.rag_service import (
    build_context_text,
    build_source_citations,
    generate_quality_checked_rag_answer,
    retrieve_context_for_question,
)
from app.schemas.api import AnswerQuery, AnswerResponse
from app.core.logging import log_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/qa", tags=["qa"])


@router.get("/answer", response_model=AnswerResponse, response_model_exclude_unset=True)
def answer_question(query: AnswerQuery = Depends()):
    started_at = perf_counter()
    context_chunks = retrieve_context_for_question(
        question=query.q,
        document_id=query.document_id,
        context_limit=query.context_limit,
        candidate_limit=query.candidate_limit,
    )

    answer_result = generate_quality_checked_rag_answer(
        question=query.q,
        context_chunks=context_chunks,
    )

    response = {
        "question": query.q,
        "document_id": query.document_id,
        "answer": answer_result["answer"],
        "quality": answer_result["quality"],
        "source_count": len(context_chunks),
        "sources": build_source_citations(context_chunks),
    }

    if query.include_context:
        response["context"] = context_chunks
        response["context_text"] = build_context_text(context_chunks)

    log_event(
        logger,
        "qa_completed",
        document_id=query.document_id,
        is_answerable=answer_result["quality"]["is_answerable"],
        source_count=len(context_chunks),
        duration_ms=round((perf_counter() - started_at) * 1000),
    )

    return response

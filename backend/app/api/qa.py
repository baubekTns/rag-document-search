from fastapi import APIRouter, Depends
import logging
from app.services.rag_service import (
    build_context_text,
    build_source_citations,
    generate_quality_checked_rag_answer,
    retrieve_context_for_question,
)
from app.schemas.api import AnswerQuery, AnswerResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/qa", tags=["qa"])


@router.get("/answer", response_model=AnswerResponse, response_model_exclude_unset=True)
def answer_question(query: AnswerQuery = Depends()):
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

    logger.info(
        "QA answer completed: question=%s document_id=%s is_answerable=%s source_count=%s",
        query.q,
        query.document_id,
        answer_result["quality"]["is_answerable"],
        len(context_chunks),
    )

    return response

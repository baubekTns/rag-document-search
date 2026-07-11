from fastapi import APIRouter, Query

from app.services.rag_service import (
    build_context_text,
    create_retrieval_preview_answer,
    retrieve_context_for_question,
)

router = APIRouter(prefix="/qa", tags=["qa"])


@router.get("/answer")
def answer_question(
    q: str = Query(..., min_length=1),
    document_id: str | None = None,
    context_limit: int = Query(default=5, ge=1, le=10),
    candidate_limit: int = Query(default=20, ge=5, le=50),
):
    context_chunks = retrieve_context_for_question(
        question=q,
        document_id=document_id,
        context_limit=context_limit,
        candidate_limit=candidate_limit,
    )

    answer = create_retrieval_preview_answer(
        question=q,
        context_chunks=context_chunks,
    )

    return {
        "question": q,
        "document_id": document_id,
        "answer": answer,
        "context_count": len(context_chunks),
        "context": context_chunks,
        "context_text": build_context_text(context_chunks),
    }
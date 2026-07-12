from typing import Any


MIN_TOP_RERANK_SCORE = 0.25
MIN_TOP_SEMANTIC_SCORE = 0.25
MIN_LEXICAL_SCORE = 0.1


def assess_context_quality(
    *,
    context_chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    if not context_chunks:
        return {
            "is_answerable": False,
            "reason": "No relevant context was retrieved.",
            "top_rerank_score": 0.0,
            "top_semantic_score": 0.0,
            "top_lexical_score": 0.0,
        }

    top_chunk = context_chunks[0]

    top_rerank_score = float(top_chunk.get("rerank_score") or 0.0)
    top_semantic_score = float(top_chunk.get("semantic_score") or 0.0)
    top_lexical_score = float(top_chunk.get("lexical_score") or 0.0)

    has_enough_rerank_score = top_rerank_score >= MIN_TOP_RERANK_SCORE
    has_enough_semantic_score = top_semantic_score >= MIN_TOP_SEMANTIC_SCORE
    has_enough_lexical_score = top_lexical_score >= MIN_LEXICAL_SCORE

    is_answerable = (
        has_enough_rerank_score
        and (
            has_enough_semantic_score
            or has_enough_lexical_score
        )
    )

    if is_answerable:
        reason = "Retrieved context appears relevant enough to answer."
    else:
        reason = "Retrieved context appears too weak to answer reliably."

    return {
        "is_answerable": is_answerable,
        "reason": reason,
        "top_rerank_score": top_rerank_score,
        "top_semantic_score": top_semantic_score,
        "top_lexical_score": top_lexical_score,
        "thresholds": {
            "min_top_rerank_score": MIN_TOP_RERANK_SCORE,
            "min_top_semantic_score": MIN_TOP_SEMANTIC_SCORE,
            "min_lexical_score": MIN_LEXICAL_SCORE,
        },
    }
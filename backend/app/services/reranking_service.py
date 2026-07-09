import re
from typing import Any


SEMANTIC_WEIGHT = 0.75
LEXICAL_WEIGHT = 0.25
PHRASE_BONUS = 0.15


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        token
        for token in tokens
        if len(token) > 2
    }


def calculate_lexical_score(query: str, text: str) -> float:
    query_tokens = tokenize(query)
    text_tokens = tokenize(text)

    if not query_tokens or not text_tokens:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)

    return len(overlap) / len(query_tokens)


def calculate_phrase_bonus(query: str, text: str) -> float:
    cleaned_query = " ".join(query.lower().split())
    cleaned_text = " ".join(text.lower().split())

    if cleaned_query and cleaned_query in cleaned_text:
        return PHRASE_BONUS

    return 0.0


def rerank_chunks(
    *,
    query: str,
    candidates: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    reranked_results = []

    for candidate in candidates:
        text = candidate.get("text") or ""

        semantic_score = float(candidate.get("semantic_score") or 0.0)
        lexical_score = calculate_lexical_score(query, text)
        phrase_bonus = calculate_phrase_bonus(query, text)

        rerank_score = (
            (SEMANTIC_WEIGHT * semantic_score)
            + (LEXICAL_WEIGHT * lexical_score)
            + phrase_bonus
        )

        reranked_results.append(
            {
                **candidate,
                "lexical_score": lexical_score,
                "phrase_bonus": phrase_bonus,
                "rerank_score": rerank_score,
            }
        )

    reranked_results.sort(
        key=lambda result: result["rerank_score"],
        reverse=True,
    )

    return reranked_results[:limit]
from typing import Any


def build_rag_prompt(
    *,
    question: str,
    context_chunks: list[dict[str, Any]],
) -> str:
    context_sections = []

    for index, chunk in enumerate(context_chunks, start=1):
        context_sections.append(
            f"[Source {index}]\n"
            f"Document ID: {chunk['document_id']}\n"
            f"Chunk ID: {chunk['chunk_id']}\n"
            f"Chunk Index: {chunk['chunk_index']}\n"
            f"Text:\n{chunk['text']}"
        )

    context_text = "\n\n".join(context_sections)

    return f"""
You are an assistant for answering questions about uploaded documents.

Use only the provided context to answer the question.
If the answer is not in the context, say exactly:
"I could not find this in the uploaded documents."

Every factual sentence in your answer must cite at least one source using [Source 1], [Source 2], etc.
Do not include information that is not supported by the sources.

Question:
{question}

Context:
{context_text}

Answer with citations:
""".strip()
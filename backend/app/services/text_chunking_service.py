def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return []

    chunks: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap
    while start < len(cleaned_text):
        end = min(start + chunk_size, len(cleaned_text))
        if end < len(cleaned_text):
            boundary = cleaned_text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(cleaned_text):
            start += step
            continue
        next_start = max(end - chunk_overlap, start + 1)
        if next_start > 0 and not cleaned_text[next_start - 1].isspace():
            next_space = cleaned_text.find(" ", next_start)
            next_start = next_space + 1 if next_space != -1 else start + step
        start = next_start

    return chunks


def chunk_page_texts(
    page_texts: list[dict[str, int | str]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict[str, int | str]]:
    """Create word-aware chunks without crossing PDF page boundaries."""
    chunks: list[dict[str, int | str]] = []
    for page in page_texts:
        page_number = int(page["page_number"])
        for text in chunk_text(str(page["text"]), chunk_size, chunk_overlap):
            chunks.append({"text": text, "page_start": page_number, "page_end": page_number})
    return chunks

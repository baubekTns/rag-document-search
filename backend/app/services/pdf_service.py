from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(file_path: Path) -> dict:
    reader = PdfReader(str(file_path))

    pages_text: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text.strip())

    full_text = "\n\n".join(pages_text).strip()

    return {
        "pages": len(reader.pages),
        "characters": len(full_text),
        "text_preview": full_text[:500],
        "text": full_text,
    }
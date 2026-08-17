from pathlib import Path

from fastapi import HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def extract_pdf_text(file_path: Path) -> dict:
    try:
        reader = PdfReader(str(file_path))
    except PdfReadError:
        raise HTTPException(status_code=400, detail="Uploaded PDF could not be read")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")

    pages_text: list[str] = []
    page_texts: list[dict[str, int | str]] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        cleaned_text = text.strip()
        pages_text.append(cleaned_text)
        if cleaned_text:
            page_texts.append({"page_number": page_number, "text": cleaned_text})

    full_text = "\n\n".join(pages_text).strip()

    if not full_text:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in this PDF. It may be scanned or image-based.",
        )

    return {
        "pages": len(reader.pages),
        "characters": len(full_text),
        "text_preview": full_text[:500],
        "text": full_text,
        "page_texts": page_texts,
    }

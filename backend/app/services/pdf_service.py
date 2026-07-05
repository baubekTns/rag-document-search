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

    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text.strip())

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
    }
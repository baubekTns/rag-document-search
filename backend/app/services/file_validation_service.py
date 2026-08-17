import re
from fastapi import HTTPException, UploadFile
from app.core.settings import get_settings

ALLOWED_CONTENT_TYPES = {"application/pdf"}


def sanitize_filename(filename: str) -> str:
    """
    Converts unsafe filenames into safer names.
    Example: '../../../my file.pdf' -> 'my-file.pdf'
    """
    filename = filename.split("/")[-1].split("\\")[-1]
    filename = filename.strip()
    filename = re.sub(r"[^a-zA-Z0-9._-]", "-", filename)
    filename = re.sub(r"-+", "-", filename)

    if not filename:
        return "uploaded-document.pdf"

    return filename


def validate_pdf_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    sanitized_filename = sanitize_filename(file.filename)

    if not sanitized_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must have a .pdf extension")


def validate_pdf_signature(header: bytes) -> None:
    if not header.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

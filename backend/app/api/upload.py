from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_metadata_service import create_document_metadata
from app.services.file_validation_service import (
    MAX_FILE_SIZE_BYTES,
    sanitize_filename,
    validate_pdf_upload,
)
from app.services.pdf_service import extract_pdf_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    validate_pdf_upload(file)

    document_id = str(uuid4())
    original_filename = sanitize_filename(file.filename)
    stored_filename = f"{document_id}_{original_filename}"
    file_path = UPLOAD_DIR / stored_filename

    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="PDF file is too large. Maximum size is 10 MB",
        )

    try:
        with open(file_path, "wb") as f:
            f.write(contents)

        extraction = extract_pdf_text(file_path)

        document_metadata = create_document_metadata(
            document_id=document_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type or "application/pdf",
            file_size=file_size,
            page_count=extraction["pages"],
            character_count=extraction["characters"],
        )

        return {
            "message": "PDF uploaded, text extracted, and metadata stored successfully",
            "document": document_metadata,
            "text_preview": extraction["text_preview"],
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()
        raise

    except Exception:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail="Failed to process uploaded PDF")
from uuid import uuid4
from app.core.exceptions import AppError
from fastapi import APIRouter, File, HTTPException, UploadFile
import logging
from app.services.file_validation_service import sanitize_filename, validate_pdf_upload
from app.core.settings import get_settings
from app.schemas.api import UploadResponse
from app.services.document_ingestion_service import ingest_document

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    validate_pdf_upload(file)

    document_id = str(uuid4())
    original_filename = sanitize_filename(file.filename)
    stored_filename = f"{document_id}_{original_filename}"

    logger.info(
        "Received PDF upload: document_id=%s filename=%s",
        document_id,
        original_filename,
    )

    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        logger.warning(
            "Rejected empty PDF upload: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if file_size > get_settings().max_upload_size_bytes:
        logger.warning(
            "Rejected oversized PDF upload: document_id=%s filename=%s size=%s",
            document_id,
            original_filename,
            file_size,
        )
        raise HTTPException(
            status_code=413,
            detail="PDF file is too large. Maximum size is 10 MB",
        )

    try:
        result = ingest_document(
            document_id=document_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type or "application/pdf",
            contents=contents,
        )
        logger.info(
            "Completed PDF upload: document_id=%s stored_filename=%s size=%s",
            document_id,
            stored_filename,
            file_size,
        )
        return result

    except HTTPException:
        logger.exception(
            "Handled upload failure: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise

    except AppError:
        logger.exception(
            "Application upload failure: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise

    except Exception:
        logger.exception(
            "Unexpected upload failure: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise HTTPException(status_code=500, detail="Failed to process uploaded PDF")

from uuid import uuid4
import asyncio
from app.core.exceptions import AppError
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
import logging
from app.services.file_validation_service import sanitize_filename, validate_pdf_signature, validate_pdf_upload
from app.core.settings import get_settings
from app.schemas.api import UploadResponse
from app.services.document_ingestion_service import ingest_document

logger = logging.getLogger(__name__)
router = APIRouter()
ingestion_semaphore = asyncio.Semaphore(get_settings().ingestion_concurrency)


async def stream_upload_to_staging(file: UploadFile, staged_path) -> int:
    settings = get_settings()
    staged_path.parent.mkdir(parents=True, exist_ok=True)
    output = await run_in_threadpool(staged_path.open, "wb")
    file_size = 0
    signature = b""
    signature_checked = False
    try:
        while chunk := await file.read(settings.upload_stream_chunk_size):
            if not signature_checked:
                signature = (signature + chunk)[:5]
                if len(signature) == 5:
                    validate_pdf_signature(signature)
                    signature_checked = True
            file_size += len(chunk)
            if file_size > settings.max_upload_size_bytes:
                raise HTTPException(status_code=413, detail="PDF file is too large. Maximum size is 10 MB")
            await run_in_threadpool(output.write, chunk)
    finally:
        await run_in_threadpool(output.close)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if not signature_checked:
        validate_pdf_signature(signature)
    return file_size

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

    staged_path = get_settings().upload_staging_directory / f"{document_id}.part"

    try:
        file_size = await stream_upload_to_staging(file, staged_path)
        async with ingestion_semaphore:
            result = await run_in_threadpool(
                ingest_document,
                document_id=document_id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                content_type=file.content_type or "application/pdf",
                staged_path=staged_path,
                file_size=file_size,
            )
        logger.info(
            "Completed PDF upload: document_id=%s stored_filename=%s size=%s",
            document_id,
            stored_filename,
            file_size,
        )
        return result

    except HTTPException:
        staged_path.unlink(missing_ok=True)
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

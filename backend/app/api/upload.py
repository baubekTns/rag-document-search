from uuid import uuid4
import asyncio
from app.core.exceptions import AppError
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
import logging
from time import perf_counter
from app.services.file_validation_service import sanitize_filename, validate_pdf_signature, validate_pdf_upload
from app.core.settings import get_settings
from app.schemas.api import UploadResponse
from app.services.document_ingestion_service import ingest_document
from app.core.logging import log_error_event, log_event

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

    started_at = perf_counter()
    log_event(logger, "upload_received", document_id=document_id)

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
        log_event(
            logger, "upload_completed", document_id=document_id, file_size=file_size,
            chunk_count=result["chunking"]["chunk_count"],
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
        return result

    except HTTPException:
        staged_path.unlink(missing_ok=True)
        log_event(logger, "upload_failed", document_id=document_id, error_category="validation")
        raise

    except AppError as error:
        log_event(logger, "upload_failed", document_id=document_id, error_category=type(error).__name__)
        raise

    except Exception:
        log_error_event(logger, "upload_failed", document_id=document_id, error_category="unexpected")
        raise HTTPException(status_code=500, detail="Failed to process uploaded PDF")

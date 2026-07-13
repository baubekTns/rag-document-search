from pathlib import Path
from uuid import uuid4
from app.core.exceptions import AppError
from fastapi import APIRouter, File, HTTPException, UploadFile
import logging
from app.services.chunk_metadata_service import create_document_chunks
from app.services.document_metadata_service import create_document_metadata
from app.services.embedding_metadata_service import create_chunk_embeddings
from app.services.embedding_service import EMBEDDING_MODEL_NAME, generate_embeddings
from app.services.file_validation_service import (
    MAX_FILE_SIZE_BYTES,
    sanitize_filename,
    validate_pdf_upload,
)
from app.services.pdf_service import extract_pdf_text
from app.services.text_chunking_service import chunk_text
from app.services.vector_store_service import (
    QDRANT_COLLECTION_NAME,
    store_chunk_vectors,
)

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    validate_pdf_upload(file)

    document_id = str(uuid4())
    original_filename = sanitize_filename(file.filename)
    stored_filename = f"{document_id}_{original_filename}"
    file_path = UPLOAD_DIR / stored_filename

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

    if file_size > MAX_FILE_SIZE_BYTES:
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
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(
            "Saved uploaded PDF: document_id=%s stored_filename=%s size=%s",
            document_id,
            stored_filename,
            file_size,
        )

        extraction = extract_pdf_text(file_path)

        logger.info(
            "Extracted PDF text: document_id=%s pages=%s characters=%s",
            document_id,
            extraction["pages"],
            extraction["characters"],
        )

        document_metadata = create_document_metadata(
            document_id=document_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type or "application/pdf",
            file_size=file_size,
            page_count=extraction["pages"],
            character_count=extraction["characters"],
        )

        chunks = chunk_text(
            extraction["text"],
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        chunk_records = create_document_chunks(
            document_id=document_id,
            chunks=chunks,
        )

        logger.info(
            "Created document chunks: document_id=%s chunk_count=%s",
            document_id,
            len(chunk_records),
        )

        embeddings = generate_embeddings(chunks)

        embedding_records = create_chunk_embeddings(
            document_id=document_id,
            chunk_records=chunk_records,
            embeddings=embeddings,
            model_name=EMBEDDING_MODEL_NAME,
        )

        logger.info(
            "Generated embeddings: document_id=%s embedding_count=%s model=%s",
            document_id,
            len(embedding_records),
            EMBEDDING_MODEL_NAME,
        )

        vector_count = store_chunk_vectors(
            document_id=document_id,
            chunk_records=chunk_records,
            embeddings=embeddings,
            model_name=EMBEDDING_MODEL_NAME,
        )

        logger.info(
            "Stored vectors: document_id=%s vector_count=%s",
            document_id,
            vector_count,
        )

        return {
            "message": "PDF uploaded, text extracted, chunked, indexed, embedded, and stored in vector database successfully",
            "document": document_metadata,
            "chunking": {
                "chunk_count": len(chunk_records),
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
            },
            "embeddings": {
                "embedding_count": len(embedding_records),
                "model_name": EMBEDDING_MODEL_NAME,
                "embedding_dimension": embedding_records[0]["embedding_dimension"]
                if embedding_records
                else 0,
            },
            "vector_storage": {
                "stored_vector_count": vector_count,
                "collection_name": QDRANT_COLLECTION_NAME,
            },
            "text_preview": extraction["text_preview"],
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        logger.exception(
            "Handled upload failure: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise

    except AppError:
        if file_path.exists():
            file_path.unlink()

        logger.exception(
            "Application upload failure: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise

    except Exception:
        if file_path.exists():
            file_path.unlink()

        logger.exception(
            "Unexpected upload failure: document_id=%s filename=%s",
            document_id,
            original_filename,
        )
        raise HTTPException(status_code=500, detail="Failed to process uploaded PDF")
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_metadata_service import create_document_metadata
from app.services.pdf_service import extract_pdf_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    document_id = str(uuid4())
    stored_filename = f"{document_id}_{file.filename}"
    file_path = UPLOAD_DIR / stored_filename

    contents = await file.read()
    file_size = len(contents)

    with open(file_path, "wb") as f:
        f.write(contents)

    extraction = extract_pdf_text(file_path)

    document_metadata = create_document_metadata(
        document_id=document_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_size=file_size,
        page_count=extraction["pages"],
        character_count=extraction["characters"],
    )

    return {
        "message": "PDF uploaded, text extracted, and metadata stored successfully",
        "document": document_metadata,
        "text_preview": extraction["text_preview"],
    }
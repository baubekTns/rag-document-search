from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.pdf_service import extract_pdf_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    extraction = extract_pdf_text(file_path)

    return {
        "message": "PDF uploaded and text extracted successfully",
        "filename": file.filename,
        "stored_as": file_path.name,
        "pages": extraction["pages"],
        "characters": extraction["characters"],
        "text_preview": extraction["text_preview"],
    }
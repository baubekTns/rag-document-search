from fastapi import APIRouter, HTTPException

from app.services.document_metadata_service import (
    get_document_metadata,
    list_document_metadata,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
def list_documents():
    return {"documents": list_document_metadata()}


@router.get("/{document_id}")
def get_document(document_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"document": document}
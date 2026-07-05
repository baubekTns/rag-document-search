from fastapi import APIRouter, HTTPException

from app.services.chunk_metadata_service import (
    get_chunk_by_id,
    list_chunk_previews_for_document,
)
from app.services.document_metadata_service import (
    get_document_metadata,
    list_document_metadata,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
def list_documents():
    return {"documents": list_document_metadata()}


@router.get("/{document_id}/chunks")
def get_document_chunks(document_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = list_chunk_previews_for_document(document_id)

    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


@router.get("/{document_id}/chunks/{chunk_id}")
def get_document_chunk(document_id: str, chunk_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    chunk = get_chunk_by_id(document_id, chunk_id)

    if chunk is None:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {"chunk": chunk}


@router.get("/{document_id}")
def get_document(document_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"document": document}
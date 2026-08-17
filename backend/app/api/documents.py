from fastapi import APIRouter, HTTPException
from app.services.embedding_metadata_service import list_embedding_metadata_for_document

from app.services.chunk_metadata_service import (
    get_chunk_by_id,
    list_chunk_previews_for_document,
)
from app.services.document_metadata_service import (
    get_document_metadata,
    list_document_metadata,
)
from app.schemas.api import (
    ChunkResponse, DocumentChunksResponse, DocumentEmbeddingsResponse,
    DocumentResponse, DocumentsResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=DocumentsResponse)
def list_documents():
    return {"documents": list_document_metadata()}

@router.get("/{document_id}/chunks", response_model=DocumentChunksResponse)
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


@router.get("/{document_id}/chunks/{chunk_id}", response_model=ChunkResponse)
def get_document_chunk(document_id: str, chunk_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    chunk = get_chunk_by_id(document_id, chunk_id)

    if chunk is None:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {"chunk": chunk}

@router.get("/{document_id}/embeddings", response_model=DocumentEmbeddingsResponse)
def get_document_embeddings(document_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    embeddings = list_embedding_metadata_for_document(document_id)

    return {
        "document_id": document_id,
        "embedding_count": len(embeddings),
        "embeddings": embeddings,
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str):
    document = get_document_metadata(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"document": document}

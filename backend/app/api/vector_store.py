from fastapi import APIRouter

from app.services.vector_store_service import (
    QDRANT_COLLECTION_NAME,
    count_vectors,
)
from app.schemas.api import VectorStoreStatusResponse

router = APIRouter(prefix="/vector-store", tags=["vector-store"])


@router.get("/status", response_model=VectorStoreStatusResponse)
def get_vector_store_status():
    return {
        "collection_name": QDRANT_COLLECTION_NAME,
        "vector_count": count_vectors(),
    }

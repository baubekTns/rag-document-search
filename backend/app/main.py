from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import AppError
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.upload import router as upload_router
from app.services.chunk_metadata_service import (
    initialize_chunk_keyword_index,
    initialize_document_chunks_table,
)
from app.services.document_metadata_service import initialize_document_metadata_table
from app.services.embedding_metadata_service import initialize_chunk_embeddings_table
from app.services.vector_store_service import initialize_vector_collection
from app.api.vector_store import router as vector_store_router
from app.api.qa import router as qa_router
from app.core.logging_config import configure_logging
from app.core.database import initialize_schema_version, transaction
from app.core.settings import get_settings
from app.schemas.api import RootResponse
from app.core.error_handlers import app_error_handler

configure_logging()
app = FastAPI()
app.add_exception_handler(AppError, app_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with transaction() as connection:
    initialize_schema_version(connection)
    initialize_document_metadata_table(connection)
    initialize_document_chunks_table(connection)
    initialize_chunk_keyword_index(connection)
    initialize_chunk_embeddings_table(connection)
initialize_vector_collection()

app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(vector_store_router)
app.include_router(qa_router)


@app.get("/", response_model=RootResponse)
def root():
    return {"status": "ok"}

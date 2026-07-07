from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.upload import router as upload_router
from app.services.chunk_metadata_service import (
    initialize_chunk_keyword_index,
    initialize_document_chunks_table,
)
from app.services.document_metadata_service import initialize_document_metadata_table
from app.services.embedding_metadata_service import initialize_chunk_embeddings_table

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_document_metadata_table()
initialize_document_chunks_table()
initialize_chunk_keyword_index()
initialize_chunk_embeddings_table()

app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(search_router)


@app.get("/")
def root():
    return {"status": "ok"}
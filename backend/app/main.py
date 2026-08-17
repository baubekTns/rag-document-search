from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
from app.core.database import apply_schema_migrations, initialize_schema_version, transaction
from app.core.settings import get_settings
from app.schemas.api import ReadinessResponse, RootResponse
from app.core.error_handlers import app_error_handler
from app.core.logging import request_id_context
from app.services.health_service import readiness_report

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    with transaction() as connection:
        initialize_schema_version(connection)
        initialize_document_metadata_table(connection)
        initialize_document_chunks_table(connection)
        initialize_chunk_keyword_index(connection)
        initialize_chunk_embeddings_table(connection)
        apply_schema_migrations(connection)
    initialize_vector_collection()
    yield


def create_app() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    application.add_exception_handler(AppError, app_error_handler)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(get_settings().cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def request_correlation_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        token = request_id_context.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_context.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response

    application.include_router(upload_router)
    application.include_router(documents_router)
    application.include_router(search_router)
    application.include_router(vector_store_router)
    application.include_router(qa_router)

    @application.get("/", response_model=RootResponse)
    def root():
        return {"status": "ok"}

    @application.get("/health/live", response_model=RootResponse)
    def liveness():
        return {"status": "ok"}

    @application.get("/health/ready", response_model=ReadinessResponse)
    def readiness():
        ready, dependencies = readiness_report()
        content = ReadinessResponse(
            status="ready" if ready else "not_ready", dependencies=dependencies
        ).model_dump()
        return JSONResponse(status_code=200 if ready else 503, content=content)

    return application

app = create_app()

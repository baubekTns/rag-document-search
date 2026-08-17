from typing import Any

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str


class KeywordSearchQuery(BaseModel):
    q: str = Field(min_length=1)
    document_id: str | None = None
    limit: int = Field(default=10, ge=1, le=50)


class SemanticSearchQuery(BaseModel):
    q: str = Field(min_length=1)
    document_id: str | None = None
    limit: int = Field(default=5, ge=1, le=20)


class RerankedSearchQuery(BaseModel):
    q: str = Field(min_length=1)
    document_id: str | None = None
    limit: int = Field(default=5, ge=1, le=20)
    candidate_limit: int = Field(default=20, ge=5, le=50)


class AnswerQuery(BaseModel):
    q: str = Field(min_length=1)
    document_id: str | None = None
    context_limit: int = Field(default=5, ge=1, le=10)
    candidate_limit: int = Field(default=20, ge=5, le=50)
    include_context: bool = False


class DocumentMetadata(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    page_count: int
    character_count: int
    uploaded_at: str
    processing_status: str


class DocumentsResponse(BaseModel):
    documents: list[DocumentMetadata]


class ChunkPreview(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    character_count: int
    created_at: str
    preview: str


class Chunk(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    chunk_text: str
    character_count: int
    created_at: str


class DocumentChunksResponse(BaseModel):
    document_id: str
    chunk_count: int
    chunks: list[ChunkPreview]


class ChunkResponse(BaseModel):
    chunk: Chunk


class EmbeddingMetadata(BaseModel):
    id: str
    chunk_id: str
    document_id: str
    model_name: str
    embedding_dimension: int
    created_at: str


class DocumentEmbeddingsResponse(BaseModel):
    document_id: str
    embedding_count: int
    embeddings: list[EmbeddingMetadata]


class DocumentResponse(BaseModel):
    document: DocumentMetadata


class KeywordSearchResult(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    character_count: int
    created_at: str
    snippet: str
    preview: str


class SemanticSearchResult(BaseModel):
    score: float
    chunk_id: str | None
    document_id: str | None
    chunk_index: int | None
    character_count: int | None
    model_name: str | None
    text: str | None


class RerankedSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    character_count: int
    model_name: str | None
    text: str
    semantic_score: float
    keyword_match: bool
    keyword_snippet: str | None = None
    lexical_score: float
    phrase_bonus: float
    rerank_score: float


class KeywordSearchResponse(BaseModel):
    query: str
    document_id: str | None
    result_count: int
    results: list[KeywordSearchResult]


class SemanticSearchResponse(BaseModel):
    query: str
    document_id: str | None
    result_count: int
    results: list[SemanticSearchResult]


class RerankedSearchResponse(BaseModel):
    query: str
    document_id: str | None
    candidate_count: int
    result_count: int
    results: list[RerankedSearchResult]


class Thresholds(BaseModel):
    min_top_rerank_score: float
    min_top_semantic_score: float
    min_lexical_score: float


class AnswerQuality(BaseModel):
    is_answerable: bool
    reason: str
    top_rerank_score: float
    top_semantic_score: float
    top_lexical_score: float
    thresholds: Thresholds


class Citation(BaseModel):
    source_number: int
    document_id: str
    chunk_id: str
    chunk_index: int
    preview: str
    rerank_score: float | None
    semantic_score: float | None
    keyword_match: bool | None


class AnswerResponse(BaseModel):
    question: str
    document_id: str | None
    answer: str
    quality: AnswerQuality
    source_count: int
    sources: list[Citation]
    context: list[dict[str, Any]] | None = None
    context_text: str | None = None


class UploadChunking(BaseModel):
    chunk_count: int
    chunk_size: int
    chunk_overlap: int


class UploadEmbeddings(BaseModel):
    embedding_count: int
    model_name: str
    embedding_dimension: int


class UploadVectorStorage(BaseModel):
    stored_vector_count: int
    collection_name: str


class UploadResponse(BaseModel):
    message: str
    document: DocumentMetadata
    chunking: UploadChunking
    embeddings: UploadEmbeddings
    vector_storage: UploadVectorStorage
    text_preview: str


class VectorStoreStatusResponse(BaseModel):
    collection_name: str
    vector_count: int

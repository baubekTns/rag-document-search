export interface DocumentMetadata {
  id: string;
  original_filename: string;
  stored_filename: string;
  content_type: string;
  file_size: number;
  page_count: number;
  character_count: number;
  uploaded_at: string;
}

export interface ChunkingMetadata {
  chunk_count: number;
  chunk_size: number;
  chunk_overlap: number;
}

export interface EmbeddingMetadata {
  embedding_count: number;
  model_name: string;
  embedding_dimension: number;
}

export interface UploadResponse {
  message: string;
  document: DocumentMetadata;
  chunking: ChunkingMetadata;
  embeddings: EmbeddingMetadata;
  vector_storage: VectorStorageMetadata;
  text_preview: string;
}

export interface ApiErrorResponse {
  detail?: string;
}

export interface VectorStorageMetadata {
  stored_vector_count: number;
  collection_name: string;
}

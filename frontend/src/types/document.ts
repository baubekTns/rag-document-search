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

export interface UploadResponse {
  message: string;
  document: DocumentMetadata;
  chunking: ChunkingMetadata;
  text_preview: string;
}

export interface ApiErrorResponse {
  detail?: string;
}

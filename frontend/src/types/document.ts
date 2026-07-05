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

export interface UploadResponse {
  message: string;
  document: DocumentMetadata;
  text_preview: string;
}

export interface ApiErrorResponse {
  detail?: string;
}

import type { UploadResponse } from "../../types/document";
import { ProcessingDetails } from "./ProcessingDetails";

interface UploadSummaryProps {
  result: UploadResponse;
}

export function UploadSummary({ result }: UploadSummaryProps) {
  return (
    <div>
      <h3>Document Metadata</h3>
      <p><strong>Filename:</strong> {result.document.original_filename}</p>
      <p><strong>Pages:</strong> {result.document.page_count}</p>
      <p><strong>Characters:</strong> {result.document.character_count}</p>

      <h3>Chunking</h3>
      <p><strong>Chunks:</strong> {result.chunking.chunk_count}</p>
      <p><strong>Chunk size:</strong> {result.chunking.chunk_size}</p>
      <p><strong>Chunk overlap:</strong> {result.chunking.chunk_overlap}</p>

      <h3>Text Preview</h3>
      <p>{result.text_preview}</p>

      <ProcessingDetails result={result} />
    </div>
  );
}

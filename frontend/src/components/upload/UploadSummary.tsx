import type { UploadResponse } from "../../types/document";
import { ProcessingDetails } from "./ProcessingDetails";

interface UploadSummaryProps {
  result: UploadResponse;
}

export function UploadSummary({ result }: UploadSummaryProps) {
  return (
    <div className="upload-summary">
      <h3>Document Metadata</h3>
      <dl className="metadata-list">
        <div><dt>Filename</dt><dd>{result.document.original_filename}</dd></div>
        <div><dt>Pages</dt><dd>{result.document.page_count}</dd></div>
        <div><dt>Characters</dt><dd>{result.document.character_count}</dd></div>
      </dl>

      <h3>Chunking</h3>
      <dl className="metadata-list">
        <div><dt>Chunks</dt><dd>{result.chunking.chunk_count}</dd></div>
        <div><dt>Chunk size</dt><dd>{result.chunking.chunk_size}</dd></div>
        <div><dt>Chunk overlap</dt><dd>{result.chunking.chunk_overlap}</dd></div>
      </dl>

      <h3>Text Preview</h3>
      <p className="text-preview">{result.text_preview}</p>

      <ProcessingDetails result={result} />
    </div>
  );
}

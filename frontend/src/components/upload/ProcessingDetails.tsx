import type { UploadResponse } from "../../types/document";

interface ProcessingDetailsProps {
  result: UploadResponse;
}

export function ProcessingDetails({ result }: ProcessingDetailsProps) {
  return (
    <details className="processing-details">
      <summary>Processing details</summary>

      <h3>Embeddings</h3>
      <dl className="metadata-list">
        <div><dt>Embeddings</dt><dd>{result.embeddings.embedding_count}</dd></div>
        <div><dt>Model</dt><dd>{result.embeddings.model_name}</dd></div>
        <div><dt>Dimension</dt><dd>{result.embeddings.embedding_dimension}</dd></div>
      </dl>

      <h3>Vector Storage</h3>
      <dl className="metadata-list">
        <div><dt>Stored vectors</dt><dd>{result.vector_storage.stored_vector_count}</dd></div>
        <div><dt>Collection</dt><dd>{result.vector_storage.collection_name}</dd></div>
      </dl>
    </details>
  );
}

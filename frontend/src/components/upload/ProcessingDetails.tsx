import type { UploadResponse } from "../../types/document";

interface ProcessingDetailsProps {
  result: UploadResponse;
}

export function ProcessingDetails({ result }: ProcessingDetailsProps) {
  return (
    <details>
      <summary>Processing details</summary>

      <h3>Embeddings</h3>
      <p><strong>Embeddings:</strong> {result.embeddings.embedding_count}</p>
      <p><strong>Model:</strong> {result.embeddings.model_name}</p>
      <p><strong>Dimension:</strong> {result.embeddings.embedding_dimension}</p>

      <h3>Vector Storage</h3>
      <p><strong>Stored vectors:</strong> {result.vector_storage.stored_vector_count}</p>
      <p><strong>Collection:</strong> {result.vector_storage.collection_name}</p>
    </details>
  );
}

import type { DocumentMetadata } from "../../types/document";
import type { RequestStatus } from "../../hooks/useAbortableRequest";

interface DocumentSelectorProps {
  label: string;
  documents: DocumentMetadata[];
  selectedDocumentId: string | null;
  status: RequestStatus;
  error: Error | null;
  onSelect: (documentId: string | null) => void;
  onRetry: () => void;
}

export function DocumentSelector({
  label,
  documents,
  selectedDocumentId,
  status,
  error,
  onSelect,
  onRetry,
}: DocumentSelectorProps) {
  const activeDocument = selectedDocumentId
    ? documents.find((document) => document.id === selectedDocumentId) ?? null
    : null;

  return (
    <div>
      <label>
        {label} scope
        <select
          value={selectedDocumentId ?? ""}
          onChange={(event) => onSelect(event.target.value || null)}
          disabled={status === "loading"}
        >
          <option value="">All documents</option>
          {documents.map((document) => (
            <option key={document.id} value={document.id}>
              {document.original_filename}
            </option>
          ))}
        </select>
      </label>

      <p>Active scope: {activeDocument ? activeDocument.original_filename : "All documents"}</p>
      {status === "loading" && <p>Loading available documents...</p>}
      {status === "success" && documents.length === 0 && <p>No documents uploaded yet.</p>}
      {status === "error" && error && (
        <p>
          {error.message} <button onClick={onRetry}>Retry</button>
        </p>
      )}
    </div>
  );
}

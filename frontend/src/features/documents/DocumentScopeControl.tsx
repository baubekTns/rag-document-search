import { useDocumentWorkspace } from "./useDocumentWorkspace";

interface DocumentScopeControlProps {
  label: string;
}

export function DocumentScopeControl({ label }: DocumentScopeControlProps) {
  const {
    documents,
    documentStatus,
    documentError,
    selectedDocumentId,
    selectedDocument,
    setSelectedDocumentId,
    refreshDocuments,
  } = useDocumentWorkspace();

  return (
    <div>
      <label>
        {label} scope
        <select
          value={selectedDocumentId ?? ""}
          onChange={(event) => setSelectedDocumentId(event.target.value || null)}
          disabled={documentStatus === "loading"}
        >
          <option value="">All documents</option>
          {documents.map((document) => (
            <option key={document.id} value={document.id}>
              {document.original_filename}
            </option>
          ))}
        </select>
      </label>

      <p>
        Active scope: {selectedDocument ? selectedDocument.original_filename : "All documents"}
      </p>

      {documentStatus === "loading" && <p>Loading available documents...</p>}
      {documentStatus === "success" && documents.length === 0 && (
        <p>No documents uploaded yet.</p>
      )}
      {documentStatus === "error" && documentError && (
        <p>
          {documentError.message} <button onClick={() => void refreshDocuments()}>Retry</button>
        </p>
      )}
    </div>
  );
}

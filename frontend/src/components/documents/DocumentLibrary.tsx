import { useDocumentWorkspace } from "../../features/documents/useDocumentWorkspace";
import { DocumentSelector } from "./DocumentSelector";

export function DocumentLibrary() {
  const workspace = useDocumentWorkspace();

  return (
    <section className="document-library" aria-labelledby="document-library-title">
      <div className="panel-heading">
        <p className="eyebrow">Workspace</p>
        <h2 id="document-library-title">Document library</h2>
        <p>Choose the documents that searches and answers should use.</p>
      </div>
      <DocumentSelector
        label="Search scope"
        documents={workspace.documents}
        selectedDocumentId={workspace.selectedDocumentId}
        status={workspace.documentStatus}
        error={workspace.documentError}
        onSelect={workspace.setSelectedDocumentId}
        onRetry={() => void workspace.refreshDocuments()}
      />
    </section>
  );
}

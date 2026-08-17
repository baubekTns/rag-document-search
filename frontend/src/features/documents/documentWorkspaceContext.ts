import { createContext } from "react";
import type { RequestStatus } from "../../hooks/useAbortableRequest";
import type { DocumentMetadata } from "../../types/document";

export interface DocumentWorkspaceValue {
  documents: DocumentMetadata[];
  documentStatus: RequestStatus;
  documentError: Error | null;
  selectedDocumentId: string | null;
  selectedDocument: DocumentMetadata | null;
  setSelectedDocumentId: (documentId: string | null) => void;
  addDocument: (document: DocumentMetadata) => void;
  refreshDocuments: () => Promise<void>;
}

export const DocumentWorkspaceContext = createContext<DocumentWorkspaceValue | null>(null);

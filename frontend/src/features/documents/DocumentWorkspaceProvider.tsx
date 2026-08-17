import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { DocumentWorkspaceContext } from "./documentWorkspaceContext";
import { listDocuments } from "../../services/documentService";
import type { DocumentMetadata } from "../../types/document";
import type { RequestStatus } from "../../hooks/useAbortableRequest";

function toError(error: unknown): Error {
  return error instanceof Error
    ? error
    : new Error("Unable to load documents. Please try again.");
}

export function DocumentWorkspaceProvider({ children }: { children: ReactNode }) {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [documentStatus, setDocumentStatus] = useState<RequestStatus>("idle");
  const [documentError, setDocumentError] = useState<Error | null>(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);

  const refreshDocuments = useCallback(async () => {
    controllerRef.current?.abort();

    const controller = new AbortController();
    const requestId = requestIdRef.current + 1;

    controllerRef.current = controller;
    requestIdRef.current = requestId;
    setDocumentError(null);
    setDocumentStatus("loading");

    try {
      const response = await listDocuments(controller.signal);

      if (controller.signal.aborted || requestId !== requestIdRef.current) {
        return;
      }

      setDocuments(response.documents);
      setSelectedDocumentId((currentSelection) =>
        currentSelection && response.documents.some((document) => document.id === currentSelection)
          ? currentSelection
          : null,
      );
      setDocumentStatus("success");
    } catch (error) {
      if (controller.signal.aborted || requestId !== requestIdRef.current) {
        return;
      }

      setDocumentError(toError(error));
      setDocumentStatus("error");
    } finally {
      if (requestId === requestIdRef.current) {
        controllerRef.current = null;
      }
    }
  }, []);

  useEffect(() => {
    void refreshDocuments();

    return () => {
      controllerRef.current?.abort();
    };
  }, [refreshDocuments]);

  const addDocument = useCallback((document: DocumentMetadata) => {
    requestIdRef.current += 1;
    controllerRef.current?.abort();
    controllerRef.current = null;
    setDocuments((currentDocuments) => [
      document,
      ...currentDocuments.filter((currentDocument) => currentDocument.id !== document.id),
    ]);
    setDocumentError(null);
    setDocumentStatus("success");
  }, []);

  return (
    <DocumentWorkspaceContext.Provider
      value={{
        documents,
        documentStatus,
        documentError,
        selectedDocumentId,
        setSelectedDocumentId,
        addDocument,
        refreshDocuments,
      }}
    >
      {children}
    </DocumentWorkspaceContext.Provider>
  );
}

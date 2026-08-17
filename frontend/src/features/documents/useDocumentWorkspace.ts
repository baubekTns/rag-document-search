import { useContext } from "react";
import { DocumentWorkspaceContext } from "./documentWorkspaceContext";
import type { DocumentWorkspaceValue } from "./documentWorkspaceContext";

export function useDocumentWorkspace(): DocumentWorkspaceValue {
  const context = useContext(DocumentWorkspaceContext);

  if (!context) {
    throw new Error("useDocumentWorkspace must be used within DocumentWorkspaceProvider.");
  }

  return context;
}

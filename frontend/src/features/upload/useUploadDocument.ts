import { useAbortableRequest } from "../../hooks/useAbortableRequest";
import { uploadDocument } from "../../services/documentService";
import type { UploadResponse } from "../../types/document";

export function useUploadDocument() {
  return useAbortableRequest<[File], UploadResponse>(
    ([file], signal) => uploadDocument(file, signal),
    { clearDataOnExecute: true },
  );
}

import { requestJson } from "./apiClient";
import type { DocumentListResponse, UploadResponse } from "../types/document";

export function listDocuments(signal?: AbortSignal): Promise<DocumentListResponse> {
  return requestJson<DocumentListResponse>("/documents/", { signal });
}

export async function uploadDocument(
  file: File,
  signal?: AbortSignal,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return requestJson<UploadResponse>("/upload", {
    method: "POST",
    body: formData,
    signal,
  });
}

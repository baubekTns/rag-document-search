import { requestJson } from "./apiClient";
import type { UploadResponse } from "../types/document";

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

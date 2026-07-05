import type { ApiErrorResponse, UploadResponse } from "../types/document";

const API_BASE_URL = "http://localhost:8000";

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    const errorData = data as ApiErrorResponse;
    throw new Error(errorData.detail || "Upload failed");
  }

  return data as UploadResponse;
}

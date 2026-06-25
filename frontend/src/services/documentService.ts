import type { UploadResponse } from "../types/document";

const API_BASE_URL = "http://localhost:8000";

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/uploadfile/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }

  return response.json();
}

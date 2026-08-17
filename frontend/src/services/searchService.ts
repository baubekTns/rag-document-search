import { requestJson } from "./apiClient";
import type { SearchMode, SearchResponse } from "../types/search";

export async function searchDocuments(
  query: string,
  mode: SearchMode,
  limit = 5,
  signal?: AbortSignal,
  documentId?: string | null,
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  if (documentId) {
    params.set("document_id", documentId);
  }

  return requestJson<SearchResponse>(`/search/${mode}?${params.toString()}`, {
    signal,
  });
}

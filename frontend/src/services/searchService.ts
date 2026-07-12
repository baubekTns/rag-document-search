import type { SearchMode, SearchResponse } from "../types/search";

const API_BASE_URL = "http://localhost:8000";

export async function searchDocuments(
  query: string,
  mode: SearchMode,
  limit = 5,
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  const response = await fetch(
    `${API_BASE_URL}/search/${mode}?${params.toString()}`,
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Search failed");
  }

  return data as SearchResponse;
}

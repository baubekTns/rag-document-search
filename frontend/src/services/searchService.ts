export interface KeywordSearchResult {
  id: string;
  document_id: string;
  chunk_index: number;
  character_count: number;
  created_at: string;
  snippet: string;
  preview: string;
}

export interface KeywordSearchResponse {
  query: string;
  document_id: string | null;
  result_count: number;
  results: KeywordSearchResult[];
}

const API_BASE_URL = "http://localhost:8000";

export async function keywordSearch(
  query: string,
): Promise<KeywordSearchResponse> {
  const params = new URLSearchParams({ q: query });

  const response = await fetch(
    `${API_BASE_URL}/search/keyword?${params.toString()}`,
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Keyword search failed");
  }

  return data as KeywordSearchResponse;
}

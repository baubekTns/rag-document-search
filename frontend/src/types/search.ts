export type SearchMode = "keyword" | "semantic" | "reranked";

export interface SearchResult {
  id?: string;
  chunk_id?: string;
  document_id: string;
  chunk_index: number;
  character_count: number;
  created_at?: string;
  snippet?: string;
  preview?: string;
  text?: string;
  score?: number;
  semantic_score?: number;
  lexical_score?: number;
  phrase_bonus?: number;
  rerank_score?: number;
  keyword_match?: boolean;
  keyword_snippet?: string;
  model_name?: string | null;
}

export interface SearchResponse {
  query: string;
  document_id: string | null;
  result_count: number;
  candidate_count?: number;
  results: SearchResult[];
}

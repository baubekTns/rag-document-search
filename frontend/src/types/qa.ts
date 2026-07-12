export interface AnswerQuality {
  is_answerable: boolean;
  reason: string;
  top_rerank_score: number;
  top_semantic_score: number;
  top_lexical_score: number;
  thresholds: {
    min_top_rerank_score: number;
    min_top_semantic_score: number;
    min_lexical_score: number;
  };
}

export interface AnswerSource {
  source_number: number;
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  preview: string;
  rerank_score: number;
  semantic_score: number;
  keyword_match: boolean;
}

export interface QaAnswerResponse {
  question: string;
  document_id: string | null;
  answer: string;
  quality: AnswerQuality;
  source_count: number;
  sources: AnswerSource[];
}

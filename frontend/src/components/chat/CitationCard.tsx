import type { AnswerSource } from "../../types/qa";

interface CitationCardProps {
  source: AnswerSource;
}

function formatScore(score: unknown): string {
  return typeof score === "number" && Number.isFinite(score) ? score.toFixed(3) : "Not available";
}

export function CitationCard({ source }: CitationCardProps) {
  return (
    <details className="citation-card">
      <summary>Source {source.source_number} — supporting passage</summary>
      <p><strong>Document ID:</strong> {source.document_id}</p>
      <p><strong>Chunk ID:</strong> {source.chunk_id}</p>
      <p><strong>Chunk index:</strong> {source.chunk_index}</p>
      <p><strong>Rerank score:</strong> {formatScore(source.rerank_score)}</p>
      <p><strong>Semantic score:</strong> {formatScore(source.semantic_score)}</p>
      <p><strong>Keyword match:</strong> {source.keyword_match ? "Yes" : "No"}</p>
      <p><strong>Preview:</strong></p>
      <blockquote>{source.preview}</blockquote>
    </details>
  );
}

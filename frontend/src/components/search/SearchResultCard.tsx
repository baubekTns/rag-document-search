import type { SearchResult } from "../../types/search";

interface SearchResultCardProps {
  result: SearchResult;
  index: number;
}

function formatScore(score: unknown): string | null {
  return typeof score === "number" && Number.isFinite(score) ? score.toFixed(3) : null;
}

export function SearchResultCard({ result, index }: SearchResultCardProps) {
  const displayText = result.snippet || result.keyword_snippet || result.preview || result.text || "";
  const scores = [
    ["Semantic score", formatScore(result.score)],
    ["Semantic score", formatScore(result.semantic_score)],
    ["Lexical score", formatScore(result.lexical_score)],
    ["Rerank score", formatScore(result.rerank_score)],
  ] as const;

  return (
    <article>
      <h4>Result {index + 1}</h4>
      <p><strong>Document:</strong> {result.document_id}</p>
      <p><strong>Chunk index:</strong> {result.chunk_index}</p>

      {scores.map(([label, score], scoreIndex) =>
        score ? <p key={`${label}-${scoreIndex}`}><strong>{label}:</strong> {score}</p> : null,
      )}

      {result.keyword_match !== undefined && (
        <p><strong>Keyword match:</strong> {result.keyword_match ? "Yes" : "No"}</p>
      )}

      <p>{displayText}</p>
    </article>
  );
}

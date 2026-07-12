import type { AnswerSource } from "../types/qa";

interface CitationViewerProps {
  sources: AnswerSource[];
}

export default function CitationViewer({ sources }: CitationViewerProps) {
  if (sources.length === 0) {
    return <p>No sources returned.</p>;
  }

  return (
    <div>
      <h4>Sources</h4>

      {sources.map((source) => (
        <details key={source.chunk_id}>
          <summary>
            Source {source.source_number} — chunk {source.chunk_index}
          </summary>

          <p>
            <strong>Document ID:</strong> {source.document_id}
          </p>

          <p>
            <strong>Chunk ID:</strong> {source.chunk_id}
          </p>

          <p>
            <strong>Chunk index:</strong> {source.chunk_index}
          </p>

          <p>
            <strong>Rerank score:</strong> {source.rerank_score.toFixed(3)}
          </p>

          <p>
            <strong>Semantic score:</strong> {source.semantic_score.toFixed(3)}
          </p>

          <p>
            <strong>Keyword match:</strong>{" "}
            {source.keyword_match ? "Yes" : "No"}
          </p>

          <p>
            <strong>Preview:</strong>
          </p>

          <blockquote>{source.preview}</blockquote>
        </details>
      ))}
    </div>
  );
}

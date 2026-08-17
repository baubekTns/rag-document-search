import type { AnswerSource } from "../../types/qa";
import { CitationCard } from "./CitationCard";

interface CitationListProps {
  sources: AnswerSource[];
}

export function CitationList({ sources }: CitationListProps) {
  if (sources.length === 0) {
    return <p>No sources returned.</p>;
  }

  return (
    <div>
      <h4>Sources</h4>
      {sources.map((source) => <CitationCard key={source.chunk_id} source={source} />)}
    </div>
  );
}

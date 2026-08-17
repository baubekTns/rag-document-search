import type { SearchMode, SearchResponse } from "../../types/search";
import { SearchResultCard } from "./SearchResultCard";

interface SearchResultsProps {
  result: SearchResponse;
  mode: SearchMode;
}

export function SearchResults({ result, mode }: SearchResultsProps) {
  return (
    <div className="search-results">
      <h3>Results</h3>
      <div className="result-summary">
        <p><strong>Mode:</strong> {mode}</p>
        <p><strong>Results:</strong> {result.result_count}</p>
      </div>
      {result.candidate_count !== undefined && (
        <p className="result-summary"><strong>Candidates:</strong> {result.candidate_count}</p>
      )}

      {result.results.length === 0 ? (
        <p className="empty-state">No results found.</p>
      ) : (
        result.results.map((searchResult, index) => {
          const key = searchResult.chunk_id || searchResult.id || `${searchResult.document_id}-${index}`;

          return <SearchResultCard key={key} result={searchResult} index={index} />;
        })
      )}
    </div>
  );
}

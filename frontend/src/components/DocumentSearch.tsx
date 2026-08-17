import { useState } from "react";
import { useDocumentSearch } from "../features/search/useDocumentSearch";
import type { SearchMode } from "../types/search";

export default function DocumentSearch() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<SearchMode>("reranked");
  const [validationMessage, setValidationMessage] = useState("");
  const { data: searchResult, error, status, execute } = useDocumentSearch();
  const loading = status === "loading";

  const handleSearch = async () => {
    if (!query.trim()) {
      setValidationMessage("Please enter a search query.");
      return;
    }

    setValidationMessage("");
    await execute(query.trim(), mode);
  };

  return (
    <section>
      <h2>Search Documents</h2>

      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search uploaded documents..."
        disabled={loading}
      />

      <select
        value={mode}
        onChange={(event) => setMode(event.target.value as SearchMode)}
        disabled={loading}
      >
        <option value="keyword">Keyword</option>
        <option value="semantic">Semantic</option>
        <option value="reranked">Reranked</option>
      </select>

      <button onClick={handleSearch} disabled={loading || !query.trim()}>
        {loading ? "Searching..." : "Search"}
      </button>

      {validationMessage && <p>{validationMessage}</p>}
      {error && <p>{error.message}</p>}

      {searchResult && (
        <div>
          <h3>Results</h3>

          <p>
            <strong>Mode:</strong> {mode}
          </p>

          <p>
            <strong>Results:</strong> {searchResult.result_count}
          </p>

          {searchResult.candidate_count !== undefined && (
            <p>
              <strong>Candidates:</strong> {searchResult.candidate_count}
            </p>
          )}

          {searchResult.results.length === 0 ? (
            <p>No results found.</p>
          ) : (
            searchResult.results.map((result, index) => {
              const resultKey =
                result.chunk_id ||
                result.id ||
                `${result.document_id}-${index}`;

              const displayText =
                result.snippet ||
                result.keyword_snippet ||
                result.preview ||
                result.text ||
                "";

              return (
                <article key={resultKey}>
                  <h4>Result {index + 1}</h4>

                  <p>
                    <strong>Document:</strong> {result.document_id}
                  </p>

                  <p>
                    <strong>Chunk index:</strong> {result.chunk_index}
                  </p>

                  {result.score !== undefined && (
                    <p>
                      <strong>Semantic score:</strong> {result.score.toFixed(3)}
                    </p>
                  )}

                  {result.semantic_score !== undefined && (
                    <p>
                      <strong>Semantic score:</strong>{" "}
                      {result.semantic_score.toFixed(3)}
                    </p>
                  )}

                  {result.lexical_score !== undefined && (
                    <p>
                      <strong>Lexical score:</strong>{" "}
                      {result.lexical_score.toFixed(3)}
                    </p>
                  )}

                  {result.rerank_score !== undefined && (
                    <p>
                      <strong>Rerank score:</strong>{" "}
                      {result.rerank_score.toFixed(3)}
                    </p>
                  )}

                  {result.keyword_match !== undefined && (
                    <p>
                      <strong>Keyword match:</strong>{" "}
                      {result.keyword_match ? "Yes" : "No"}
                    </p>
                  )}

                  <p>{displayText}</p>
                </article>
              );
            })
          )}
        </div>
      )}
    </section>
  );
}

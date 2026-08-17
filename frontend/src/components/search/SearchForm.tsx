import type { SearchMode } from "../../types/search";

interface SearchFormProps {
  query: string;
  mode: SearchMode;
  loading: boolean;
  onQueryChange: (query: string) => void;
  onModeChange: (mode: SearchMode) => void;
  onSubmit: () => void;
  describedBy?: string;
}

export function SearchForm({
  query,
  mode,
  loading,
  onQueryChange,
  onModeChange,
  onSubmit,
  describedBy,
}: SearchFormProps) {
  return (
    <form className="search-form" onSubmit={(event) => { event.preventDefault(); onSubmit(); }} aria-busy={loading}>
      <label className="field-label" htmlFor="document-search-query">
        Search query
        <input
          id="document-search-query"
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search uploaded documents..."
          autoComplete="off"
          aria-describedby={describedBy}
          aria-invalid={Boolean(describedBy)}
          disabled={loading}
        />
      </label>

      <label className="field-label" htmlFor="document-search-mode">
        Search mode
        <select
          id="document-search-mode"
          value={mode}
          onChange={(event) => onModeChange(event.target.value as SearchMode)}
          autoComplete="off"
          disabled={loading}
        >
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
          <option value="reranked">Reranked</option>
        </select>
      </label>

      <button className="button button-secondary" type="submit" disabled={loading || !query.trim()}>
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}

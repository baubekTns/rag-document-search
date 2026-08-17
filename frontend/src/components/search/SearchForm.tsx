import type { SearchMode } from "../../types/search";

interface SearchFormProps {
  query: string;
  mode: SearchMode;
  loading: boolean;
  onQueryChange: (query: string) => void;
  onModeChange: (mode: SearchMode) => void;
  onSubmit: () => void;
}

export function SearchForm({
  query,
  mode,
  loading,
  onQueryChange,
  onModeChange,
  onSubmit,
}: SearchFormProps) {
  return (
    <>
      <input
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        placeholder="Search uploaded documents..."
        disabled={loading}
      />

      <select
        value={mode}
        onChange={(event) => onModeChange(event.target.value as SearchMode)}
        disabled={loading}
      >
        <option value="keyword">Keyword</option>
        <option value="semantic">Semantic</option>
        <option value="reranked">Reranked</option>
      </select>

      <button onClick={onSubmit} disabled={loading || !query.trim()}>
        {loading ? "Searching..." : "Search"}
      </button>
    </>
  );
}

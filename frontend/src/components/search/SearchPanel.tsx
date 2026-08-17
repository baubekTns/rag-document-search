import { useState } from "react";
import { useDocumentWorkspace } from "../../features/documents/useDocumentWorkspace";
import { useDocumentSearch } from "../../features/search/useDocumentSearch";
import type { SearchMode } from "../../types/search";
import { SearchForm } from "./SearchForm";
import { SearchResults } from "./SearchResults";

export function SearchPanel() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<SearchMode>("reranked");
  const [validationMessage, setValidationMessage] = useState("");
  const { data: searchResult, error, status, execute } = useDocumentSearch();
  const workspace = useDocumentWorkspace();
  const loading = status === "loading";

  const handleSearch = async () => {
    if (!query.trim()) {
      setValidationMessage("Please enter a search query.");
      return;
    }

    setValidationMessage("");
    await execute(query.trim(), mode, workspace.selectedDocumentId);
  };

  return (
    <section className="panel search-panel" aria-labelledby="search-title">
      <div className="panel-heading panel-heading-inline">
        <div>
          <p className="eyebrow">Explore</p>
          <h2 id="search-title">Search documents</h2>
          <p>Inspect the passages that retrieval finds most relevant.</p>
        </div>
        <p className="scope-pill">Scope: {workspace.scopeLabel}</p>
      </div>
      <SearchForm
        query={query}
        mode={mode}
        loading={loading}
        onQueryChange={setQuery}
        onModeChange={setMode}
        onSubmit={() => void handleSearch()}
      />

      {validationMessage && <p className="feedback feedback-error">{validationMessage}</p>}
      {error && <p className="feedback feedback-error">{error.message}</p>}
      {loading && <p className="feedback feedback-loading">Searching documents...</p>}
      {searchResult && <SearchResults result={searchResult} mode={mode} />}
    </section>
  );
}

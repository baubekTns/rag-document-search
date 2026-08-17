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
  const [cancellationMessage, setCancellationMessage] = useState("");
  const { data: searchResult, error, status, execute, cancel } = useDocumentSearch();
  const workspace = useDocumentWorkspace();
  const loading = status === "loading";

  const handleSearch = async () => {
    if (!query.trim()) {
      setValidationMessage("Please enter a search query.");
      return;
    }

    setValidationMessage("");
    setCancellationMessage("");
    await execute(query.trim(), mode, workspace.selectedDocumentId);
  };

  const handleCancel = () => {
    cancel();
    setCancellationMessage("Search cancelled. Previous results are still available.");
  };

  const errorMessage = validationMessage || error?.message;

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
        describedBy={errorMessage ? "search-error" : undefined}
      />

      {loading && <button className="button button-tertiary cancel-action" type="button" onClick={handleCancel}>Cancel search</button>}
      {errorMessage && <p id="search-error" className="feedback feedback-error" role="alert">{errorMessage}</p>}
      {loading && <p className="feedback feedback-loading" role="status" aria-live="polite">Searching documents...</p>}
      {cancellationMessage && <p className="feedback feedback-loading" role="status" aria-live="polite">{cancellationMessage}</p>}
      {searchResult && <SearchResults result={searchResult} mode={mode} />}
    </section>
  );
}

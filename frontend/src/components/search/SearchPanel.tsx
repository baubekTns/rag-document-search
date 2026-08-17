import { useState } from "react";
import { DocumentSelector } from "../documents/DocumentSelector";
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
    <section>
      <h2>Search Documents</h2>
      <DocumentSelector
        label="Search"
        documents={workspace.documents}
        selectedDocumentId={workspace.selectedDocumentId}
        status={workspace.documentStatus}
        error={workspace.documentError}
        onSelect={workspace.setSelectedDocumentId}
        onRetry={() => void workspace.refreshDocuments()}
      />
      <SearchForm
        query={query}
        mode={mode}
        loading={loading}
        onQueryChange={setQuery}
        onModeChange={setMode}
        onSubmit={() => void handleSearch()}
      />

      {validationMessage && <p>{validationMessage}</p>}
      {error && <p>{error.message}</p>}
      {searchResult && <SearchResults result={searchResult} mode={mode} />}
    </section>
  );
}

import { useAbortableRequest } from "../../hooks/useAbortableRequest";
import { searchDocuments } from "../../services/searchService";
import type { SearchMode, SearchResponse } from "../../types/search";

export function useDocumentSearch() {
  return useAbortableRequest<[string, SearchMode, string | null], SearchResponse>(
    ([query, mode, documentId], signal) =>
      searchDocuments(query, mode, 5, signal, documentId),
  );
}

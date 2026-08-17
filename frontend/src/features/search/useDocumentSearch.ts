import { useAbortableRequest } from "../../hooks/useAbortableRequest";
import { searchDocuments } from "../../services/searchService";
import type { SearchMode, SearchResponse } from "../../types/search";

export function useDocumentSearch() {
  return useAbortableRequest<[string, SearchMode], SearchResponse>(
    ([query, mode], signal) => searchDocuments(query, mode, 5, signal),
  );
}

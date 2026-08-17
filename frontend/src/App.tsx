import { ChatPanel } from "./components/chat/ChatPanel";
import { DocumentLibrary } from "./components/documents/DocumentLibrary";
import { SearchPanel } from "./components/search/SearchPanel";
import { UploadPanel } from "./components/upload/UploadPanel";
import { DocumentWorkspaceProvider } from "./features/documents/DocumentWorkspaceProvider";

function App() {
  return (
    <DocumentWorkspaceProvider>
      <div className="app-shell">
        <header className="app-header">
          <div>
            <p className="eyebrow">RAG workspace</p>
            <h1>Document Intelligence</h1>
            <p>Search your PDFs, ask grounded questions, and review the evidence behind every answer.</p>
          </div>
          <p className="app-badge">AI document search</p>
        </header>

        <div className="workspace-grid">
          <aside className="workspace-sidebar">
            <DocumentLibrary />
            <UploadPanel />
          </aside>

          <main className="workspace-content">
            <ChatPanel />
            <SearchPanel />
          </main>
        </div>
      </div>
    </DocumentWorkspaceProvider>
  );
}

export default App;

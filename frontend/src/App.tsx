import { ChatPanel } from "./components/chat/ChatPanel";
import { SearchPanel } from "./components/search/SearchPanel";
import { UploadPanel } from "./components/upload/UploadPanel";
import { DocumentWorkspaceProvider } from "./features/documents/DocumentWorkspaceProvider";

function App() {
  return (
    <DocumentWorkspaceProvider>
      <main>
        <h1>AI Document Search</h1>

        <UploadPanel />

        <SearchPanel />

        <ChatPanel />
      </main>
    </DocumentWorkspaceProvider>
  );
}

export default App;

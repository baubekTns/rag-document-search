import ChatInterface from "./components/ChatInterface";
import DocumentSearch from "./components/DocumentSearch";
import DocumentUpload from "./components/DocumentUpload";
import { DocumentWorkspaceProvider } from "./features/documents/DocumentWorkspaceProvider";

function App() {
  return (
    <DocumentWorkspaceProvider>
      <main>
        <h1>AI Document Search</h1>

        <DocumentUpload />

        <DocumentSearch />

        <ChatInterface />
      </main>
    </DocumentWorkspaceProvider>
  );
}

export default App;

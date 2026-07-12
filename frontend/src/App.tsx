import ChatInterface from "./components/ChatInterface";
import DocumentSearch from "./components/DocumentSearch";
import DocumentUpload from "./components/DocumentUpload";

function App() {
  return (
    <main>
      <h1>AI Document Search</h1>

      <DocumentUpload />

      <DocumentSearch />

      <ChatInterface />
    </main>
  );
}

export default App;

import DocumentSearch from "./components/DocumentSearch";
import DocumentUpload from "./components/DocumentUpload";
import QuestionAnswer from "./components/QuestionAnswer";

function App() {
  return (
    <main>
      <h1>AI Document Search</h1>

      <DocumentUpload />

      <DocumentSearch />

      <QuestionAnswer />
    </main>
  );
}

export default App;

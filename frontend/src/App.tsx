import { useEffect, useState } from "react";
import { testBackend } from "./api";
import DocumentUpload from "./components/DocumentUpload";

function App() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    testBackend().then(setData);
  }, []);

  return (
    <div>
      <h1>AI Document Search</h1>

      <DocumentUpload />
    </div>
  );
}

export default App;

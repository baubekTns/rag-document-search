import { useEffect, useState } from "react";
import { testBackend } from "./api";

function App() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    testBackend().then(setData);
  }, []);

  return (
    <div>
      <h1>AI Document Search Platform</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default App;

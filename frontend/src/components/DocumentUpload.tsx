import { useState } from "react";
import { uploadDocument } from "../services/documentService";

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [uploading, setUploading] = useState(false);

  const [message, setMessage] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);
    setMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a PDF.");
      return;
    }

    try {
      setUploading(true);

      const result = await uploadDocument(selectedFile);

      setMessage(`Uploaded: ${result.filename}`);
    } catch {
      setMessage("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h2>Upload Document</h2>

      <input type="file" accept=".pdf" onChange={handleFileChange} />

      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? "Uploading..." : "Upload"}
      </button>

      {message && <p>{message}</p>}
    </div>
  );
}

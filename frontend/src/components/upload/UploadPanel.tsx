import { useState } from "react";
import { useDocumentWorkspace } from "../../features/documents/useDocumentWorkspace";
import { useUploadDocument } from "../../features/upload/useUploadDocument";
import { UploadSummary } from "./UploadSummary";

export function UploadPanel() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationMessage, setValidationMessage] = useState("");
  const { data: uploadResult, error, status, execute, reset } = useUploadDocument();
  const { addDocument } = useDocumentWorkspace();
  const uploading = status === "loading";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    reset();

    if (!file) {
      setSelectedFile(null);
      setValidationMessage("");
      return;
    }

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setSelectedFile(null);
      setValidationMessage("Please select a PDF file.");
      return;
    }

    setSelectedFile(file);
    setValidationMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setValidationMessage("Please select a PDF file first.");
      return;
    }

    setValidationMessage("");
    const result = await execute(selectedFile);

    if (result) {
      addDocument(result.document);
    }
  };

  return (
    <section>
      <h2>Upload Document</h2>

      <input
        type="file"
        accept="application/pdf,.pdf"
        onChange={handleFileChange}
        disabled={uploading}
      />

      <button onClick={handleUpload} disabled={uploading || !selectedFile}>
        {uploading ? "Uploading..." : "Upload"}
      </button>

      {validationMessage && <p>{validationMessage}</p>}
      {error && <p>{error.message}</p>}
      {status === "success" && <p>PDF uploaded and chunked successfully.</p>}
      {uploadResult && <UploadSummary result={uploadResult} />}
    </section>
  );
}

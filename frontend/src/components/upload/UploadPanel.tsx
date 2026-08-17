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
    <section className="panel upload-panel" aria-labelledby="upload-title">
      <div className="panel-heading">
        <p className="eyebrow">Ingest</p>
        <h2 id="upload-title">Upload a document</h2>
        <p>Add a PDF to make it available across the workspace.</p>
      </div>

      <div className="upload-controls">
        <input
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileChange}
          disabled={uploading}
        />

        <button className="button button-secondary" onClick={handleUpload} disabled={uploading || !selectedFile}>
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {validationMessage && <p className="feedback feedback-error">{validationMessage}</p>}
      {error && <p className="feedback feedback-error">{error.message}</p>}
      {uploading && <p className="feedback feedback-loading">Processing document...</p>}
      {status === "success" && <p className="feedback feedback-success">PDF uploaded and chunked successfully.</p>}
      {uploadResult && <UploadSummary result={uploadResult} />}
    </section>
  );
}

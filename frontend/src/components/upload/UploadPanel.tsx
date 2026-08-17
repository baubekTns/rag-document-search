import { useState } from "react";
import { useDocumentWorkspace } from "../../features/documents/useDocumentWorkspace";
import { useUploadDocument } from "../../features/upload/useUploadDocument";
import { UploadSummary } from "./UploadSummary";

export function UploadPanel() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationMessage, setValidationMessage] = useState("");
  const [cancellationMessage, setCancellationMessage] = useState("");
  const { data: uploadResult, error, status, execute, reset, cancel } = useUploadDocument();
  const { addDocument } = useDocumentWorkspace();
  const uploading = status === "loading";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    reset();
    setCancellationMessage("");

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
    setCancellationMessage("");
  };

  const handleCancel = () => {
    cancel();
    setCancellationMessage("Upload cancelled.");
  };

  const errorMessage = validationMessage || error?.message;

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

      <form className="upload-controls" onSubmit={(event) => { event.preventDefault(); void handleUpload(); }} aria-busy={uploading}>
        <label className="field-label" htmlFor="document-upload">
          PDF document
          <input
            id="document-upload"
            type="file"
            accept="application/pdf,.pdf"
            onChange={handleFileChange}
            aria-describedby={errorMessage ? "upload-error" : undefined}
            aria-invalid={Boolean(errorMessage)}
            disabled={uploading}
          />
        </label>

        <button className="button button-secondary" type="submit" disabled={uploading || !selectedFile}>
          {uploading ? "Uploading..." : "Upload"}
        </button>
        {uploading && <button className="button button-tertiary" type="button" onClick={handleCancel}>Cancel</button>}
      </form>

      {errorMessage && <p id="upload-error" className="feedback feedback-error" role="alert">{errorMessage}</p>}
      {uploading && <p className="feedback feedback-loading" role="status" aria-live="polite">Processing document...</p>}
      {cancellationMessage && <p className="feedback feedback-loading" role="status" aria-live="polite">{cancellationMessage}</p>}
      {status === "success" && <p className="feedback feedback-success" role="status" aria-live="polite">PDF uploaded and chunked successfully.</p>}
      {uploadResult && <UploadSummary result={uploadResult} />}
    </section>
  );
}

import { useState } from "react";
import { uploadDocument } from "../services/documentService";
import type { UploadResponse } from "../types/document";

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    setUploadResult(null);

    if (!file) {
      setSelectedFile(null);
      setMessage("");
      return;
    }

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setSelectedFile(null);
      setMessage("Please select a PDF file.");
      return;
    }

    setSelectedFile(file);
    setMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a PDF file first.");
      return;
    }

    try {
      setUploading(true);
      setMessage("");
      setUploadResult(null);

      const result = await uploadDocument(selectedFile);

      setUploadResult(result);
      setMessage("PDF uploaded and chunked successfully.");
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Upload failed. Please try again.";

      setMessage(errorMessage);
    } finally {
      setUploading(false);
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

      {message && <p>{message}</p>}

      {uploadResult && (
        <div>
          <h3>Document Metadata</h3>

          <p>
            <strong>Filename:</strong> {uploadResult.document.original_filename}
          </p>

          <p>
            <strong>Pages:</strong> {uploadResult.document.page_count}
          </p>

          <p>
            <strong>Characters:</strong> {uploadResult.document.character_count}
          </p>

          <h3>Chunking</h3>

          <p>
            <strong>Chunks:</strong> {uploadResult.chunking.chunk_count}
          </p>

          <p>
            <strong>Chunk size:</strong> {uploadResult.chunking.chunk_size}
          </p>

          <h3>Embeddings</h3>

          <p>
            <strong>Embeddings:</strong>{" "}
            {uploadResult.embeddings.embedding_count}
          </p>

          <p>
            <strong>Model:</strong> {uploadResult.embeddings.model_name}
          </p>

          <p>
            <strong>Dimension:</strong>{" "}
            {uploadResult.embeddings.embedding_dimension}
          </p>

          <p>
            <strong>Chunk overlap:</strong>{" "}
            {uploadResult.chunking.chunk_overlap}
          </p>

          <h3>Text Preview</h3>
          <p>{uploadResult.text_preview}</p>
        </div>
      )}
    </section>
  );
}

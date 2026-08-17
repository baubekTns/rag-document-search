import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { DocumentMetadata, UploadResponse } from "./types/document";
import type { QaAnswerResponse } from "./types/qa";
import type { SearchResponse } from "./types/search";

const services = vi.hoisted(() => ({
  listDocuments: vi.fn(),
  uploadDocument: vi.fn(),
  searchDocuments: vi.fn(),
  askQuestion: vi.fn(),
}));

vi.mock("./services/documentService", () => ({
  listDocuments: services.listDocuments,
  uploadDocument: services.uploadDocument,
}));
vi.mock("./services/searchService", () => ({ searchDocuments: services.searchDocuments }));
vi.mock("./services/qaService", () => ({ askQuestion: services.askQuestion }));

const documentOne: DocumentMetadata = {
  id: "document-1",
  original_filename: "contract.pdf",
  stored_filename: "document-1_contract.pdf",
  content_type: "application/pdf",
  file_size: 200,
  page_count: 2,
  character_count: 1000,
  uploaded_at: "2026-01-01T00:00:00Z",
};

const searchResponse: SearchResponse = {
  query: "payment",
  document_id: null,
  result_count: 1,
  results: [{ document_id: "document-1", chunk_index: 0, character_count: 100, text: "Payment is due monthly.", score: 0.9 }],
};

const answerResponse: QaAnswerResponse = {
  question: "What is due?",
  document_id: null,
  answer: "Payment is due monthly.",
  quality: { is_answerable: true, reason: "Relevant context found.", top_rerank_score: 0.9, top_semantic_score: 0.9, top_lexical_score: 0.8 },
  source_count: 1,
  sources: [{ source_number: 1, document_id: "document-1", chunk_id: "chunk-1", chunk_index: 0, preview: "Payment is due monthly.", rerank_score: 0.9, semantic_score: 0.8, keyword_match: true }],
};

function uploadResponse(document: DocumentMetadata): UploadResponse {
  return {
    message: "Uploaded",
    document,
    chunking: { chunk_count: 1, chunk_size: 1000, chunk_overlap: 200 },
    embeddings: { embedding_count: 1, model_name: "test-model", embedding_dimension: 384 },
    vector_storage: { stored_vector_count: 1, collection_name: "chunks" },
    text_preview: "A document preview.",
  };
}

describe("document workspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    services.listDocuments.mockResolvedValue({ documents: [documentOne] });
    services.searchDocuments.mockResolvedValue(searchResponse);
    services.askQuestion.mockResolvedValue(answerResponse);
  });

  it("uses all documents by default and sends a selected document scope", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("option", { name: "contract.pdf" });

    await user.type(screen.getByLabelText("Search query"), "payment");
    await user.click(screen.getByRole("button", { name: "Search" }));
    await waitFor(() => expect(services.searchDocuments).toHaveBeenLastCalledWith("payment", "reranked", 5, expect.any(AbortSignal), null));

    await user.selectOptions(screen.getByLabelText("Search scope"), "document-1");
    await user.clear(screen.getByLabelText("Search query"));
    await user.type(screen.getByLabelText("Search query"), "payment again");
    await user.click(screen.getByRole("button", { name: "Search" }));
    await waitFor(() => expect(services.searchDocuments).toHaveBeenLastCalledWith("payment again", "reranked", 5, expect.any(AbortSignal), "document-1"));
  });

  it("renders search success, empty results, errors, retryable hook state, and cancellation feedback", async () => {
    const user = userEvent.setup();
    services.searchDocuments.mockResolvedValueOnce(searchResponse).mockResolvedValueOnce({ ...searchResponse, result_count: 0, results: [] }).mockRejectedValueOnce(new Error("Search unavailable"));
    render(<App />);
    await screen.findByRole("option", { name: "contract.pdf" });

    const query = screen.getByLabelText("Search query");
    await user.type(query, "payment");
    await user.keyboard("{Enter}");
    expect(await screen.findByText("Payment is due monthly.")).toBeInTheDocument();

    await user.clear(query);
    await user.type(query, "none");
    await user.keyboard("{Enter}");
    expect(await screen.findByText("No results found.")).toBeInTheDocument();

    await user.clear(query);
    await user.type(query, "failure");
    await user.keyboard("{Enter}");
    expect(await screen.findByRole("alert")).toHaveTextContent("Search unavailable");
  });

  it("announces search cancellation while retaining the prior result card", async () => {
    const user = userEvent.setup();
    services.searchDocuments.mockResolvedValueOnce(searchResponse).mockImplementationOnce(() => new Promise(() => {}));
    render(<App />);
    await screen.findByRole("option", { name: "contract.pdf" });

    const query = screen.getByLabelText("Search query");
    await user.type(query, "payment");
    await user.keyboard("{Enter}");
    expect(await screen.findByText("Payment is due monthly.")).toBeInTheDocument();

    await user.clear(query);
    await user.type(query, "another search");
    await user.keyboard("{Enter}");
    expect(await screen.findByRole("button", { name: "Cancel search" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cancel search" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Search cancelled. Previous results are still available.");
    expect(screen.getByText("Payment is due monthly.")).toBeInTheDocument();
  });

  it("validates uploads, reports upload failure, and adds successful uploads to the library", async () => {
    const user = userEvent.setup();
    const uploadedDocument = { ...documentOne, id: "document-2", original_filename: "report.pdf" };
    services.uploadDocument.mockRejectedValueOnce(new Error("Upload failed")).mockResolvedValueOnce(uploadResponse(uploadedDocument));
    render(<App />);
    await screen.findByRole("option", { name: "contract.pdf" });

    const fileInput = screen.getByLabelText("PDF document");
    fireEvent.change(fileInput, { target: { files: [new File(["text"], "notes.txt", { type: "text/plain" })] } });
    expect(await screen.findByRole("alert")).toHaveTextContent("Please select a PDF file.");

    fireEvent.change(fileInput, { target: { files: [new File(["pdf"], "report.pdf", { type: "application/pdf" })] } });
    await user.click(screen.getByRole("button", { name: "Upload" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Upload failed");

    await user.click(screen.getByRole("button", { name: "Upload" }));
    expect(await screen.findByRole("status", { name: "" })).toHaveTextContent("PDF uploaded and chunked successfully.");
    expect(await screen.findByRole("option", { name: "report.pdf" })).toBeInTheDocument();
  });

  it("preserves conversation, renders refusals, and safely displays nullable citation scores", async () => {
    const user = userEvent.setup();
    const refusal: QaAnswerResponse = {
      ...answerResponse,
      question: "Unknown question",
      answer: "I could not find this in the uploaded documents.",
      quality: { ...answerResponse.quality, is_answerable: false, reason: "No relevant context was retrieved." },
      sources: [{ ...answerResponse.sources[0], rerank_score: null, semantic_score: undefined as unknown as null }],
    };
    services.askQuestion
      .mockResolvedValueOnce(answerResponse)
      .mockResolvedValueOnce(refusal)
      .mockRejectedValueOnce(new Error("Question service unavailable"));
    render(<App />);
    await screen.findByRole("option", { name: "contract.pdf" });

    const question = screen.getByLabelText("Your question");
    await user.type(question, "What is due?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect((await screen.findAllByText("Payment is due monthly.")).length).toBeGreaterThan(0);

    await user.type(question, "Unknown question");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByText("I could not find this in the uploaded documents.")).toBeInTheDocument();
    expect(screen.getAllByText("Payment is due monthly.").length).toBeGreaterThan(0);
    await user.click(screen.getAllByText(/Source 1 — supporting passage/)[1]);
    expect(screen.getAllByText("Not available")).toHaveLength(2);

    await user.type(question, "Will this fail?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Question service unavailable");
  });
});

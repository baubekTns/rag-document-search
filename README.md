# rag-document-search

A Retrieval-Augmented Generation (RAG) application that allows users to upload documents and query them using natural language. The system combines semantic search, vector embeddings, and Large Language Models (LLMs) to provide accurate, document-grounded answers with source citations.

---

## Project Status

### Phase 1: Foundation

- [x] Repository initialized
- [x] Project roadmap defined
- [x] Backend service setup
- [x] Frontend service setup
- [x] Docker environment

### Phase 2: Document Ingestion

- [x] PDF upload endpoint
- [x] PDF text extraction
- [x] Document metadata storage
- [x] Error handling and validation

### Phase 3: Search Foundation

- [x] Text chunking
- [x] Chunk metadata storage
- [x] Keyword search index
- [x] Embedding generation
- [x] Production embedding model
- [x] Vector storage
- [x] Similarity search
- [x] Re-ranking

### Phase 4: Question Answering

- [x] Retrieval pipeline
- [x] LLM integration
- [x] Context-aware answer generation
- [x] Source citations
- [x] Answer quality checks

### Phase 5: User Interface

- [x] Upload workflow
- [x] Search workflow
- [x] Question answering workflow
- [x] Source preview display
- [ ] Chat interface
- [ ] Citation viewer

### Phase 6: Production Readiness

- [ ] Automated tests
- [ ] Logging and monitoring
- [ ] Docker deployment
- [ ] CI/CD pipeline

### Stretch Goals

- [ ] OCR support for scanned documents
- [ ] Authentication and user accounts
- [ ] Multi-document collections
- [ ] Hybrid search (keyword + semantic)
- [ ] Document summarization
- [ ] Conversation memory

---

## Overview

The goal of this project is to build a production-style AI search platform capable of understanding document content rather than relying solely on keyword matching.

Users can:

- Upload PDF documents
- Ask questions in natural language
- Retrieve relevant document passages
- Receive grounded AI-generated answers
- View supporting citations

Example queries:

> What are the payment obligations in this contract?

> Summarize the security requirements across all uploaded documents.

> Which sections mention GDPR compliance?

---

# Architecture

## Design Goals

- Fast semantic search
- Accurate retrieval
- Grounded answer generation
- Modular system design
- Easy deployment
- Extensible architecture

---

## Technology Stack

| Layer               | Technology            |
| ------------------- | --------------------- |
| Frontend            | React + TypeScript    |
| Backend             | FastAPI               |
| Relational Database | PostgreSQL            |
| Vector Database     | Qdrant                |
| Embeddings          | Sentence Transformers |
| LLM                 | Ollama                |
| Deployment          | Docker                |

---

## High-Level Architecture

Architecture diagram will be added in a future update.

```
User
  │
  ▼
Frontend (React)
  │
  ▼
Backend API (FastAPI)
  │
  ├── PostgreSQL
  ├── Qdrant
  └── LLM Provider
```

---

## Document Ingestion Flow

```
PDF Upload
    │
    ▼
Text Extraction
    │
    ▼
Chunking
    │
    ▼
Embedding Generation
    │
    ▼
Vector Storage
```

---

## Query Flow

```
Question
    │
    ▼
Embedding Generation
    │
    ▼
Vector Search
    │
    ▼
Top-K Relevant Chunks
    │
    ▼
Prompt Construction
    │
    ▼
LLM
    │
    ▼
Answer + Citations
```

---

## Core Components

### Frontend

Responsibilities:

- Document upload
- Search interface
- Chat experience
- Citation display

### Backend

Responsibilities:

- API endpoints
- Document processing
- Retrieval orchestration
- Authentication (future)

### Vector Database

Responsibilities:

- Store embeddings
- Perform similarity search
- Metadata filtering

### LLM Service

Responsibilities:

- Context-aware answer generation
- Summarization
- Citation generation

---

## Design Decisions

### Why FastAPI?

- Modern Python framework
- Automatic API documentation
- Async support
- Popular in AI applications

### Why PostgreSQL?

- Reliable relational database
- Strong ecosystem
- Production-ready
- Suitable for metadata and user management

### Why Qdrant?

- Open-source vector database
- Efficient similarity search
- Easy local development
- Production deployment support

### Why RAG Instead of Fine-Tuning?

RAG allows the model to retrieve up-to-date information directly from uploaded documents without retraining. This reduces hallucinations and improves answer grounding.

---

## Data Model (Initial)

### Document

```text
id
filename
upload_timestamp
file_size
```

### Chunk

```text
id
document_id
chunk_text
page_number
```

### Embedding

```text
chunk_id
vector
```

---

## Future Improvements

- OCR support for scanned PDFs
- Authentication and authorization
- Multi-user support
- Hybrid retrieval
- Streaming responses
- Local LLM support
- Analytics dashboard

---

## Local Development

Setup instructions will be added once the backend and frontend foundations are complete.

---

## License

MIT License

class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        public_message: str = "An internal service error occurred",
    ):
        self.message = message
        self.status_code = status_code
        self.public_message = public_message
        super().__init__(message)


class EmbeddingGenerationError(AppError):
    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(message, status_code=500, public_message="Embedding generation failed")


class VectorStoreError(AppError):
    def __init__(self, message: str = "Vector store operation failed"):
        super().__init__(message, status_code=502, public_message="Vector search is temporarily unavailable")


class LLMServiceError(AppError):
    def __init__(self, message: str = "LLM service unavailable"):
        super().__init__(message, status_code=502, public_message="Answer generation is temporarily unavailable")

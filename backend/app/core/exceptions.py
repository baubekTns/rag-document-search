class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EmbeddingGenerationError(AppError):
    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(message, status_code=500)


class VectorStoreError(AppError):
    def __init__(self, message: str = "Vector store operation failed"):
        super().__init__(message, status_code=502)


class LLMServiceError(AppError):
    def __init__(self, message: str = "LLM service unavailable"):
        super().__init__(message, status_code=502)
from functools import lru_cache
from threading import BoundedSemaphore

from fastembed import TextEmbedding

from app.core.exceptions import EmbeddingGenerationError
from app.core.settings import get_settings

EMBEDDING_MODEL_NAME = get_settings().embedding_model_name
embedding_semaphore = BoundedSemaphore(get_settings().embedding_concurrency)
KNOWN_EMBEDDING_DIMENSIONS = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
}


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    try:
        return TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
    except Exception as error:
        raise EmbeddingGenerationError(
            f"Failed to load embedding model: {error}"
        )


def generate_embedding(text: str) -> list[float]:
    try:
        with embedding_semaphore:
            model = get_embedding_model()
            embeddings = list(model.embed([text]))

        if not embeddings:
            raise EmbeddingGenerationError("Embedding model returned no output")

        return embeddings[0].tolist()

    except EmbeddingGenerationError:
        raise

    except Exception as error:
        raise EmbeddingGenerationError(
            f"Failed to generate query embedding: {error}"
        )


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    try:
        with embedding_semaphore:
            model = get_embedding_model()
            embeddings = list(model.embed(texts))

        return [embedding.tolist() for embedding in embeddings]

    except EmbeddingGenerationError:
        raise

    except Exception as error:
        raise EmbeddingGenerationError(
            f"Failed to generate document embeddings: {error}"
        )


@lru_cache(maxsize=1)
def get_embedding_dimension() -> int:
    """Read the configured model's known size, or probe custom models once."""
    known_dimension = KNOWN_EMBEDDING_DIMENSIONS.get(EMBEDDING_MODEL_NAME)
    if known_dimension is not None:
        return known_dimension
    return len(generate_embedding("embedding dimension probe"))

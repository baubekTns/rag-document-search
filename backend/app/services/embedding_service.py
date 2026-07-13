from functools import lru_cache

from fastembed import TextEmbedding

from app.core.exceptions import EmbeddingGenerationError


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


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
        model = get_embedding_model()
        embeddings = model.embed(texts)

        return [embedding.tolist() for embedding in embeddings]

    except EmbeddingGenerationError:
        raise

    except Exception as error:
        raise EmbeddingGenerationError(
            f"Failed to generate document embeddings: {error}"
        )
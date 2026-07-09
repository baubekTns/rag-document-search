from functools import lru_cache

from fastembed import TextEmbedding


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    return TextEmbedding(model_name=EMBEDDING_MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    embeddings = list(model.embed([text]))

    if not embeddings:
        return []

    return embeddings[0].tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.embed(texts)

    return [embedding.tolist() for embedding in embeddings]
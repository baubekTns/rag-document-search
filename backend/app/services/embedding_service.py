import hashlib
import random


EMBEDDING_MODEL_NAME = "mock-local-embedding-v1"
EMBEDDING_DIMENSION = 384


def generate_embedding(text: str) -> list[float]:
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)
    random_generator = random.Random(seed)

    return [
        random_generator.uniform(-1, 1)
        for _ in range(EMBEDDING_DIMENSION)
    ]


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    return [generate_embedding(text) for text in texts]
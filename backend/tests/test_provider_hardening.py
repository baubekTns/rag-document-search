from types import SimpleNamespace

import pytest
import requests

from app.core.exceptions import LLMServiceError, VectorStoreError
from app.services import llm_service, vector_store_service
from qdrant_client.models import Distance


def test_qdrant_client_is_reused_and_has_a_timeout(monkeypatch):
    created = []

    class Client:
        def __init__(self, **kwargs):
            created.append(kwargs)

    vector_store_service.get_qdrant_client.cache_clear()
    monkeypatch.setattr(vector_store_service, "QdrantClient", Client)

    assert vector_store_service.get_qdrant_client() is vector_store_service.get_qdrant_client()
    assert created[0]["timeout"] == 10.0
    vector_store_service.get_qdrant_client.cache_clear()


def test_existing_qdrant_collection_mismatch_fails_with_diagnostic(monkeypatch):
    collection = SimpleNamespace(
        config=SimpleNamespace(params=SimpleNamespace(vectors=SimpleNamespace(size=99, distance=Distance.COSINE)))
    )
    client = SimpleNamespace(collection_exists=lambda _: True, get_collection=lambda _: collection)
    monkeypatch.setattr(vector_store_service, "get_qdrant_client", lambda: client)
    monkeypatch.setattr(vector_store_service, "get_embedding_dimension", lambda: 2)

    with pytest.raises(VectorStoreError, match="expected size=2"):
        vector_store_service.initialize_vector_collection()


def test_ollama_timeout_retries_once_and_returns_safe_error(monkeypatch):
    calls = []
    monkeypatch.setattr(
        llm_service,
        "get_settings",
        lambda: SimpleNamespace(ollama_timeout_seconds=1, ollama_max_output_tokens=64, ollama_max_retries=1),
    )
    monkeypatch.setattr(llm_service.requests, "post", lambda *_args, **_kwargs: calls.append(1) or (_ for _ in ()).throw(requests.Timeout("private host")))
    monkeypatch.setattr(llm_service, "sleep", lambda _: None)

    with pytest.raises(LLMServiceError) as error:
        llm_service.generate_answer_with_ollama("Question")

    assert len(calls) == 2
    assert error.value.public_message == "Answer generation is temporarily unavailable"


def test_ollama_rejects_malformed_json(monkeypatch):
    response = SimpleNamespace(status_code=200, content=b"not-json", raise_for_status=lambda: None)
    response.json = lambda: (_ for _ in ()).throw(ValueError("invalid JSON"))
    monkeypatch.setattr(
        llm_service,
        "get_settings",
        lambda: SimpleNamespace(ollama_timeout_seconds=1, ollama_max_output_tokens=64, ollama_max_retries=0),
    )
    monkeypatch.setattr(llm_service.requests, "post", lambda *_args, **_kwargs: response)

    with pytest.raises(LLMServiceError, match="malformed JSON"):
        llm_service.generate_answer_with_ollama("Question")

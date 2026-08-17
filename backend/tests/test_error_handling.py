from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import VectorStoreError
from app.core.error_handlers import app_error_handler


def test_provider_error_serializes_a_safe_public_message():
    app = FastAPI()

    app.add_exception_handler(VectorStoreError, app_error_handler)

    @app.get("/failure")
    def failure():
        raise VectorStoreError("Qdrant credential for https://internal.example failed")

    response = TestClient(app).get("/failure")

    assert response.status_code == 502
    assert response.json() == {"detail": "Vector search is temporarily unavailable"}

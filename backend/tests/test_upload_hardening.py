import asyncio
import io
import threading
import time

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.api.upload import stream_upload_to_staging
from app.core.settings import get_settings
from app.services import embedding_service
from app.services.file_validation_service import validate_pdf_signature
from app.services.pdf_service import extract_pdf_text


def test_pdf_signature_rejects_non_pdf_content():
    with pytest.raises(HTTPException, match="not a valid PDF"):
        validate_pdf_signature(b"not-a-pdf")


def test_corrupted_pdf_is_rejected_after_signature_check(tmp_path):
    path = tmp_path / "corrupted.pdf"
    path.write_bytes(b"%PDF-not-really-a-pdf")

    with pytest.raises(HTTPException):
        extract_pdf_text(path)


def test_streaming_upload_stops_at_size_limit(monkeypatch, tmp_path):
    monkeypatch.setenv("MAX_UPLOAD_SIZE_BYTES", "5")
    monkeypatch.setenv("UPLOAD_STREAM_CHUNK_SIZE", "5")
    get_settings.cache_clear()
    upload = UploadFile(filename="file.pdf", file=io.BytesIO(b"%PDF-123456"), headers=Headers({"content-type": "application/pdf"}))
    target = tmp_path / "staged.part"

    with pytest.raises(HTTPException) as error:
        asyncio.run(stream_upload_to_staging(upload, target))

    assert error.value.status_code == 413
    assert target.stat().st_size <= 5
    get_settings.cache_clear()


def test_embedding_generation_is_serialized(monkeypatch):
    active = 0
    maximum = 0
    lock = threading.Lock()

    class Embedding:
        def tolist(self):
            return [0.1]

    class Model:
        def embed(self, _):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.03)
            with lock:
                active -= 1
            return [Embedding()]

    monkeypatch.setattr(embedding_service, "get_embedding_model", lambda: Model())
    threads = [threading.Thread(target=embedding_service.generate_embeddings, args=(["text"],)) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert maximum == 1

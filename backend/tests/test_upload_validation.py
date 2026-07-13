from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_rejects_non_pdf_file():
    files = {
        "file": (
            "notes.txt",
            b"This is not a PDF.",
            "text/plain",
        )
    }

    response = client.post("/upload", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"


def test_upload_rejects_empty_pdf_file():
    files = {
        "file": (
            "empty.pdf",
            b"",
            "application/pdf",
        )
    }

    response = client.post("/upload", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty"
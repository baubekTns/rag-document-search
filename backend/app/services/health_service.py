"""Safe dependency checks used by the readiness endpoint."""

import requests

from app.core.database import get_connection
from app.core.settings import get_settings
from app.services.llm_service import OLLAMA_BASE_URL
from app.services.vector_store_service import QDRANT_COLLECTION_NAME, get_qdrant_client


def check_sqlite() -> bool:
    try:
        connection = get_connection()
        try:
            connection.execute("SELECT 1")
        finally:
            connection.close()
        return True
    except Exception:
        return False


def check_qdrant() -> bool:
    try:
        get_qdrant_client().get_collection(QDRANT_COLLECTION_NAME)
        return True
    except Exception:
        return False


def check_ollama() -> bool:
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=get_settings().readiness_timeout_seconds,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def readiness_report() -> tuple[bool, dict[str, str]]:
    checks = {"sqlite": check_sqlite(), "qdrant": check_qdrant(), "ollama": check_ollama()}
    return all(checks.values()), {name: "ok" if ready else "unavailable" for name, ready in checks.items()}

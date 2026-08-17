import requests

from app.core.exceptions import LLMServiceError
from app.core.settings import get_settings


OLLAMA_BASE_URL = get_settings().ollama_base_url
OLLAMA_MODEL = get_settings().ollama_model


def generate_answer_with_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=get_settings().ollama_timeout_seconds,
        )
        response.raise_for_status()

    except requests.RequestException as error:
        raise LLMServiceError(
            f"Failed to call Ollama. Make sure Ollama is running and model '{OLLAMA_MODEL}' is available. Error: {error}"
        )

    data = response.json()
    answer = data.get("response", "").strip()

    if not answer:
        raise LLMServiceError("Ollama returned an empty answer")

    return answer

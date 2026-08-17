import requests
from time import sleep

from app.core.exceptions import LLMServiceError
from app.core.settings import get_settings


OLLAMA_BASE_URL = get_settings().ollama_base_url
OLLAMA_MODEL = get_settings().ollama_model


def generate_answer_with_ollama(prompt: str) -> str:
    settings = get_settings()
    response = None
    for attempt in range(settings.ollama_max_retries + 1):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": settings.ollama_max_output_tokens},
                },
                timeout=settings.ollama_timeout_seconds,
            )
            if response.status_code < 500 and response.status_code != 429:
                response.raise_for_status()
                break
            if attempt == settings.ollama_max_retries:
                response.raise_for_status()
        except (requests.ConnectionError, requests.Timeout) as error:
            if attempt == settings.ollama_max_retries:
                raise LLMServiceError(f"Ollama request failed: {error}")
        except requests.RequestException as error:
            raise LLMServiceError(f"Ollama returned an unsuccessful response: {error}")
        sleep(0.1)

    if response is None or not response.content:
        raise LLMServiceError("Ollama returned an empty response body")
    try:
        data = response.json()
    except ValueError as error:
        raise LLMServiceError(f"Ollama returned malformed JSON: {error}")
    answer = data.get("response", "").strip() if isinstance(data, dict) else ""

    if not answer:
        raise LLMServiceError("Ollama returned an empty answer")

    return answer

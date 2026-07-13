import os

import requests

from app.core.exceptions import LLMServiceError


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b",
)


def generate_answer_with_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
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
"""The ONLY module that talks to Groq, and the only place model names are read (D-10).

Model names change, so they come from env vars (GROQ_CLASSIFY_MODEL, GROQ_CLASSIFY_FALLBACKS,
GROQ_STT_MODEL); verify them in the Groq console on build day."""
from __future__ import annotations

import httpx

from backend.app.config import get_settings

BASE = "https://api.groq.com/openai/v1"


class GroqError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def has_key() -> bool:
    return bool(get_settings().groq_api_key)


def classify_models() -> list[str]:
    s = get_settings()
    fallbacks = [m.strip() for m in s.groq_classify_fallbacks.split(",") if m.strip()]
    return [s.groq_classify_model, *fallbacks]


def stt_model() -> str:
    return get_settings().groq_stt_model


def chat_json(model: str, system: str, user: str, timeout: float = 6.0) -> str:
    """Returns the raw assistant message content (a JSON string). Temperature 0."""
    key = get_settings().groq_api_key
    if not key:
        raise GroqError("no API key")
    try:
        r = httpx.post(
            f"{BASE}/chat/completions", timeout=timeout, headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "temperature": 0, "response_format": {"type": "json_object"},
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
    except httpx.HTTPError as e:
        raise GroqError(f"network error: {type(e).__name__}") from e
    if r.status_code != 200:
        raise GroqError(f"HTTP {r.status_code}", r.status_code)  # 429 moves to the next model
    try:
        return r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        raise GroqError("unexpected response shape") from e


def transcribe(audio: bytes, filename: str = "note.webm", language: str = "ta", timeout: float = 20.0) -> str:
    key = get_settings().groq_api_key
    if not key:
        raise GroqError("no API key")
    try:
        r = httpx.post(f"{BASE}/audio/transcriptions", timeout=timeout,
                       headers={"Authorization": f"Bearer {key}"},
                       data={"model": stt_model(), "language": language, "temperature": "0"},
                       files={"file": (filename, audio, "audio/webm")})
    except httpx.HTTPError as e:
        raise GroqError(f"network error: {type(e).__name__}") from e
    if r.status_code != 200:
        raise GroqError(f"HTTP {r.status_code}", r.status_code)
    try:
        return str(r.json()["text"]).strip()
    except (KeyError, ValueError) as e:
        raise GroqError("unexpected response shape") from e

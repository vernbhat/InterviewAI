"""Minimal client for any OpenAI-compatible chat API (Groq by default).

Bring-your-own-key: the key comes from the X-LLM-Api-Key request header, or
from LLM_API_KEY / GROQ_API_KEY on the server. Point LLM_BASE_URL at Ollama,
OpenRouter, etc. to use another provider.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_STT_MODEL = "whisper-large-v3-turbo"


class LLMError(RuntimeError):
    pass


def base_url() -> str:
    return os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def model() -> str:
    return os.getenv("LLM_MODEL", DEFAULT_MODEL)


def server_key() -> str | None:
    return os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or None


def resolve_key(header_key: str | None) -> str | None:
    key = (header_key or "").strip()
    return key or server_key()


def chat(
    messages: list[dict[str, Any]],
    key: str,
    tools: list[dict[str, Any]] | None = None,
    json_mode: bool = False,
    temperature: float = 0.4,
    max_tokens: int = 700,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    try:
        resp = httpx.post(
            f"{base_url()}/chat/completions",
            json=body,
            headers={"Authorization": f"Bearer {key}"},
            timeout=45,
        )
    except httpx.HTTPError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc
    if resp.status_code == 401:
        raise LLMError("The LLM provider rejected the API key (401).")
    if resp.status_code == 429:
        raise LLMError("LLM rate limit reached (429). Wait a minute or use another key.")
    if resp.status_code >= 400:
        raise LLMError(f"LLM error {resp.status_code}: {resp.text[:300]}")
    try:
        return resp.json()["choices"][0]["message"]
    except (KeyError, IndexError, ValueError) as exc:
        raise LLMError("Unexpected LLM response shape") from exc


def parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise LLMError("LLM did not return JSON")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise LLMError("LLM returned malformed JSON") from exc


def transcribe(audio: bytes, filename: str, content_type: str, key: str) -> str:
    try:
        resp = httpx.post(
            f"{base_url()}/audio/transcriptions",
            headers={"Authorization": f"Bearer {key}"},
            files={"file": (filename or "audio.webm", audio, content_type or "audio/webm")},
            data={"model": os.getenv("STT_MODEL", DEFAULT_STT_MODEL), "response_format": "json", "language": "en"},
            timeout=60,
        )
    except httpx.HTTPError as exc:
        raise LLMError(f"Transcription request failed: {exc}") from exc
    if resp.status_code >= 400:
        raise LLMError(f"Transcription error {resp.status_code}: {resp.text[:300]}")
    return str(resp.json().get("text", "")).strip()

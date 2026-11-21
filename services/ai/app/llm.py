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
    if provider() == "anthropic":
        return os.getenv("LLM_MODEL", "claude_sonnet_5_5")
    return os.getenv("LLM_MODEL", DEFAULT_MODEL)


def provider() -> str:
    """'openai' = any OpenAI-compatible Chat Completions API (Groq default); 'anthropic' = Messages API."""
    return os.getenv("LLM_PROVIDER", "openai").lower()


ANTHROPIC_SERVER_SENTINEL = "__server_anthropic__"


def server_key() -> str | None:
    if provider() == "anthropic":
        # The Anthropic SDK reads its own credentials (ANTHROPIC_API_KEY / platform-injected).
        return ANTHROPIC_SERVER_SENTINEL
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
    if key == ANTHROPIC_SERVER_SENTINEL:
        return _anthropic_chat(messages, tools, json_mode, temperature, max_tokens)
    body: dict[str, Any] = {
        # A user-supplied (BYOK) key always targets the OpenAI-compatible endpoint.
        "model": model() if provider() == "openai" else DEFAULT_MODEL,
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


# --------------------------------------------------------------------------- #
# Anthropic adapter: accepts/returns the OpenAI message shape used everywhere else.
# --------------------------------------------------------------------------- #

def _to_anthropic(messages: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    system: list[str] = []
    out: list[dict[str, Any]] = []

    def push(role: str, blocks: list[dict[str, Any]]) -> None:
        if out and out[-1]["role"] == role:
            out[-1]["content"].extend(blocks)
        else:
            out.append({"role": role, "content": blocks})

    for m in messages:
        role = m["role"]
        if role == "system":
            system.append(m["content"])
        elif role == "user":
            push("user", [{"type": "text", "text": m["content"] or "(empty)"}])
        elif role == "assistant":
            blocks: list[dict[str, Any]] = []
            if m.get("content"):
                blocks.append({"type": "text", "text": m["content"]})
            for tc in m.get("tool_calls") or []:
                fn = tc.get("function", {})
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                blocks.append({"type": "tool_use", "id": tc.get("id") or "call", "name": fn.get("name", ""), "input": args})
            if blocks:
                push("assistant", blocks)
        elif role == "tool":
            push("user", [{"type": "tool_result", "tool_use_id": m.get("tool_call_id") or "call", "content": m["content"]}])
    if out and out[0]["role"] != "user":
        out.insert(0, {"role": "user", "content": [{"type": "text", "text": "[The interview has started.]"}]})
    return "\n\n".join(system), out


def _anthropic_chat(messages, tools, json_mode, temperature, max_tokens) -> dict[str, Any]:
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise LLMError("LLM_PROVIDER=anthropic needs `pip install anthropic`") from exc
    system, msgs = _to_anthropic(messages)
    if json_mode:
        system += "\n\nRespond with a single JSON object only, no prose and no code fences."
    kwargs: dict[str, Any] = {"model": model(), "max_tokens": max_tokens, "system": system, "messages": msgs}
    if tools:
        kwargs["tools"] = [
            {"name": t["function"]["name"], "description": t["function"].get("description", ""), "input_schema": t["function"].get("parameters") or {"type": "object", "properties": {}}}
            for t in tools
        ]
    try:
        resp = anthropic.Anthropic(default_headers={"anthropic-version": "2023-06-01"}).messages.create(**kwargs)
    except Exception as exc:  # SDK raises many subclasses; surface them uniformly
        raise LLMError(f"LLM request failed: {type(exc).__name__}: {str(exc)[:300]}") from exc
    text_parts, calls = [], []
    for block in resp.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            calls.append({"id": block.id, "type": "function", "function": {"name": block.name, "arguments": json.dumps(block.input)}})
    message: dict[str, Any] = {"role": "assistant", "content": "".join(text_parts)}
    if calls:
        message["tool_calls"] = calls
    return message

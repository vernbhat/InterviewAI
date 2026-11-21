"""Minimal .env loader (no dependency). Real environment variables always win.

Looks for `.env` in the repo root, then in services/ai. Set INTERVIEWAI_NO_DOTENV=1 to skip.
"""

from __future__ import annotations

import os
from pathlib import Path

_HERE = Path(__file__).resolve()
CANDIDATES = [_HERE.parents[3] / ".env", _HERE.parents[1] / ".env"]


ROOT_ENV = CANDIDATES[0]
EXAMPLE = ROOT_ENV.with_name(".env.example")


def ensure_file() -> Path | None:
    """Create the repo-root .env from .env.example on first run so it's easy to find and edit."""
    if ROOT_ENV.exists() or not EXAMPLE.is_file():
        return None
    try:
        ROOT_ENV.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        return None
    return ROOT_ENV


def save_key(key: str, name: str = "GROQ_API_KEY") -> Path:
    """Write NAME=key into the repo-root .env (creating it if needed) and apply it to this process."""
    key = key.strip()
    if not key or any(c in key for c in "\r\n\"' #"):
        raise ValueError("invalid key")
    ensure_file()
    text = ROOT_ENV.read_text(encoding="utf-8") if ROOT_ENV.exists() else ""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("export "):
            stripped = stripped[7:]
        if stripped.split("=", 1)[0].strip() == name:
            lines[i] = f"{name}={key}"
            break
    else:
        lines.append(f"{name}={key}")
    ROOT_ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        ROOT_ENV.chmod(0o600)
    except OSError:
        pass
    os.environ[name] = key
    return ROOT_ENV


def can_save_key() -> bool:
    """Saving the key to disk is only offered for local installs (start.sh / npm run dev set this)."""
    return os.getenv("INTERVIEWAI_LOCAL") == "1" and not os.getenv("INTERVIEWAI_NO_DOTENV")


def load() -> list[str]:
    if os.getenv("INTERVIEWAI_NO_DOTENV"):
        return []
    ensure_file()
    loaded = []
    for path in CANDIDATES:
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[7:]
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            elif " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            if key and value and key not in os.environ:
                os.environ[key] = value
        loaded.append(str(path))
    return loaded

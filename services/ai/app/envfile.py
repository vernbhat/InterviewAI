"""Minimal .env loader (no dependency). Real environment variables always win.

Looks for `.env` in the repo root, then in services/ai. Set INTERVIEWAI_NO_DOTENV=1 to skip.
"""

from __future__ import annotations

import os
from pathlib import Path

_HERE = Path(__file__).resolve()
CANDIDATES = [_HERE.parents[3] / ".env", _HERE.parents[1] / ".env"]


def load() -> list[str]:
    if os.getenv("INTERVIEWAI_NO_DOTENV"):
        return []
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

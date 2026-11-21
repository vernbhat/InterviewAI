"""Problem bank loading and public (candidate-safe) views."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .codegen import starter_code

DATA_DIR = Path(__file__).resolve().parent / "data" / "problems"
LANGUAGES = ("cpp", "python")


@lru_cache(maxsize=1)
def _load() -> dict[str, dict[str, Any]]:
    problems = {}
    for path in sorted(DATA_DIR.glob("*.json")):
        doc = json.loads(path.read_text())
        problems[doc["id"]] = doc
    return dict(sorted(problems.items(), key=lambda kv: kv[1]["order"]))


def all_problems() -> list[dict[str, Any]]:
    return list(_load().values())


def get_problem(problem_id: str) -> dict[str, Any] | None:
    return _load().get(problem_id)


def summary(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": problem["id"],
        "title": problem["title"],
        "difficulty": problem["difficulty"],
        "pattern": problem["pattern"],
        "test_count": len(problem["tests"]),
    }


def public_view(problem: dict[str, Any]) -> dict[str, Any]:
    """Everything the candidate may see. Hidden tests and hints are excluded."""
    examples = [
        {"args": t["args"], "expected": t["expected"], "explanation": t.get("explanation", "")}
        for t in problem["tests"]
        if not t["hidden"]
    ]
    return {
        **summary(problem),
        "statement": problem["statement"],
        "constraints": problem["constraints"],
        "function": problem["function"],
        "examples": examples,
        "hidden_test_count": sum(1 for t in problem["tests"] if t["hidden"]),
        "hint_count": len(problem["hints"]),
        "starter_code": {lang: starter_code(problem, lang) for lang in LANGUAGES},
    }

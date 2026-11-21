"""Regenerate app/data/problems/*.json from scripts/problem_specs.py.

Usage (from services/ai):  python scripts/build_problems.py
"""

from __future__ import annotations

import copy
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from problem_specs import RANDOM_TESTS_PER_PROBLEM, SPECS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "app" / "data" / "problems"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()

    for order, spec in enumerate(SPECS):
        seed = int(hashlib.sha256(spec["id"].encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        ref = spec["reference"]

        def case(args, hidden, explanation=None):
            expected = ref(*copy.deepcopy(args))
            item = {"args": args, "expected": expected, "hidden": hidden}
            if explanation:
                item["explanation"] = explanation
            return item

        tests = [case(ex["args"], False, ex.get("explanation")) for ex in spec["examples"]]
        tests += [case(args, True) for args in spec["edge_cases"]]
        seen = {json.dumps(t["args"]) for t in tests}
        attempts = 0
        # Small input spaces (e.g. n <= 9) may not have enough distinct random cases; stop trying after a while.
        while sum(1 for t in tests if t["hidden"]) < len(spec["edge_cases"]) + RANDOM_TESTS_PER_PROBLEM and attempts < 500:
            attempts += 1
            args = spec["generator"](rng)
            key = json.dumps(args)
            if key not in seen:
                seen.add(key)
                tests.append(case(args, True))

        doc = {
            "id": spec["id"],
            "order": order,
            "title": spec["title"],
            "difficulty": spec["difficulty"],
            "pattern": spec["pattern"],
            "statement": spec["statement"],
            "constraints": spec["constraints"],
            "function": {
                "name": spec["function"]["name"],
                "params": [{"name": n, "type": t} for n, t in spec["function"]["params"]],
                "returns": spec["function"]["returns"],
            },
            "complexity": spec["complexity"],
            "hints": spec["hints"],
            "tests": tests,
        }
        (OUT / f"{spec['id']}.json").write_text(json.dumps(doc, indent=2) + "\n")
        print(f"{spec['id']}: {len(tests)} tests ({sum(t['hidden'] for t in tests)} hidden)")


if __name__ == "__main__":
    main()

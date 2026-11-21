"""The interviewer: a phase state machine, a hint ladder, a leak guard, and two brains.

* LLM mode: a tool-calling agent (get_test_results, give_hint, set_phase).
* Offline mode: a deterministic script used when no API key is configured. It is
  labelled as such in the UI; it never pretends to understand the candidate.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from . import llm

PHASES = ["clarify", "approach", "code", "test", "complexity", "wrapup"]
PHASE_LABELS = {
    "clarify": "Clarify the problem",
    "approach": "Discuss the approach",
    "code": "Implement",
    "test": "Test and debug",
    "complexity": "Complexity analysis",
    "wrapup": "Wrap up",
}
MAX_TOOL_ROUNDS = 4
MAX_HISTORY = 30


def advance(current: str, target: str) -> str:
    """Phases only move forward."""
    if target not in PHASES:
        return current
    return target if PHASES.index(target) > PHASES.index(current) else current


# --------------------------------------------------------------------------- #
# Leak guard
# --------------------------------------------------------------------------- #

CODE_LINE = re.compile(
    r"^\s*(def |class |for\s*\(|for .+ in .+:|while\s*[\(\w]|if\s*\(|return\b.*[;\]\)]|#include|"
    r"(int|long|auto|vector<|string|bool|unordered_map<)[\w<>,\s]*\s+\w+\s*[=\(;]|\w+(\[[^\]]*\])+\s*=[^=]|.*[;{}]\s*$)"
)


def leaks_code(text: str) -> bool:
    if "```" in text:
        return True
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return sum(1 for ln in lines if CODE_LINE.match(ln)) >= 2


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?(```|$)", "", text, flags=re.S)
    kept = [ln for ln in text.splitlines() if not CODE_LINE.match(ln)]
    return "\n".join(kept).strip()


# --------------------------------------------------------------------------- #
# Context passed to both brains
# --------------------------------------------------------------------------- #

@dataclass
class TurnContext:
    problem: dict[str, Any]
    language: str
    phase: str
    hints_used: int
    code: str
    starter: str
    history: list[dict[str, Any]]  # [{role, content}]
    last_run: dict[str, Any] | None
    last_submit: dict[str, Any] | None
    events: list[str] = field(default_factory=list)


@dataclass
class TurnResult:
    reply: str
    phase: str
    hints_used: int
    mode: str
    hint_text: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    leak_blocked: bool = False
    error: str | None = None


def run_summary(run: dict[str, Any] | None) -> dict[str, Any] | None:
    if not run:
        return None
    visible_failures = [
        {"args": t.get("args"), "expected": t.get("expected"), "actual": t.get("actual"), "error": t.get("error")}
        for t in run.get("tests", [])
        if not t.get("hidden") and not t.get("passed")
    ][:2]
    return {
        "status": run["status"],
        "passed": run["passed"],
        "total": run["total"],
        "hidden_failed": sum(1 for t in run.get("tests", []) if t.get("hidden") and not t.get("passed")),
        "visible_failures": visible_failures,
        "compile_output": (run.get("compile_output") or "")[:600],
    }


def stated_complexity(text: str) -> bool:
    return bool(re.search(r"\bO\s*\(\s*[^)]+\)", text, re.I)) or bool(
        re.search(r"\b(linear|logarithmic|quadratic|constant)\s+(time|space)\b", text, re.I)
    )


# --------------------------------------------------------------------------- #
# Offline (scripted) interviewer
# --------------------------------------------------------------------------- #

def opening_message(problem: dict[str, Any], mode: str) -> str:
    intro = (
        f"Hi, I'll be your interviewer today. The problem is **{problem['title']}** ({problem['difficulty']}). "
        "Take a moment to read it, then restate it in your own words and ask any clarifying questions "
        "about input size, edge cases or the expected output before you start coding."
    )
    if mode == "offline":
        intro += (
            "\n\n_Offline mode: no LLM key is configured, so I follow a fixed script and do not actually read "
            "your reasoning. Add a key in Settings for a real interviewer._"
        )
    return intro


def offline_turn(ctx: TurnContext, candidate_text: str) -> TurnResult:
    text = candidate_text.lower()
    phase = ctx.phase
    code_changed = ctx.code.strip() != ctx.starter.strip()
    reply: str

    if any(k in text for k in ("stuck", "hint", "no idea", "don't know", "dont know")):
        reply = "That's fine, it happens. Use the Hint button for a nudge, or tell me what you've tried so far and where it breaks."
        return TurnResult(reply, phase, ctx.hints_used, "offline")

    sub = ctx.last_submit
    run = ctx.last_run
    if sub and sub["status"] == "accepted" and phase in ("code", "test"):
        phase = "complexity"
    elif run and phase in ("clarify", "approach"):
        phase = "code"

    if phase == "clarify":
        phase = "approach"
        reply = "Good. Now walk me through your approach: what's the brute force, what does it cost, and can you do better?"
    elif phase == "approach":
        if len(candidate_text.split()) < 12:
            reply = "Can you say a bit more? Describe the algorithm step by step and the data structures you'd use."
        else:
            phase = "code"
            reply = "Sounds like a plan. Go ahead and implement it, and press Run to check the examples when you're ready."
    elif phase in ("code", "test"):
        if sub and sub["status"] != "accepted":
            phase = "test"
            reply = (
                f"Your last submission passed {sub['passed']} of {sub['total']} tests. "
                "Which inputs might your code mishandle? Think about empty, single-element, duplicate and extreme values."
            )
        elif run and run["status"] == "accepted":
            phase = "test"
            reply = "The examples pass. Before you submit, which edge cases would you test, and does your code handle them?"
        elif run:
            reply = f"Your last run ended with **{run['status'].replace('_', ' ')}** ({run['passed']}/{run['total']}). What do you think is causing it?"
        elif not code_changed:
            reply = "Whenever you're ready, start writing the code. Talk me through it as you go."
        else:
            reply = "Keep going. Run the examples once you have a first version."
    elif phase == "complexity":
        if stated_complexity(candidate_text):
            phase = "wrapup"
            reply = "Thanks. If you had more time, what would you improve or test further? When you're done, click End interview to get your report."
        else:
            reply = "All tests pass. What are the time and space complexity of your solution, and why?"
    else:
        reply = "Thanks, that's all from me. Click End interview to see your report."
    return TurnResult(reply, phase, ctx.hints_used, "offline")


# --------------------------------------------------------------------------- #
# LLM interviewer (tool-calling agent)
# --------------------------------------------------------------------------- #

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_test_results",
            "description": "Return the candidate's latest Run (visible examples) and Submit (all tests incl. hidden) results.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "give_hint",
            "description": "Reveal the next rung of the hint ladder (max 3). Only call when the candidate asks for help or has been stuck for several turns. Hints are recorded and lower the report's independence signal.",
            "parameters": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_phase",
            "description": "Move the interview forward to a later phase once the current one is done.",
            "parameters": {
                "type": "object",
                "properties": {"phase": {"type": "string", "enum": PHASES}, "reason": {"type": "string"}},
                "required": ["phase"],
            },
        },
    },
]


def system_prompt(ctx: TurnContext) -> str:
    p = ctx.problem
    lang = {"cpp": "C++", "python": "Python"}[ctx.language]
    return f"""You are a calm, rigorous technical interviewer running a 45-minute DSA coding round for a campus placement.

PROBLEM: {p['title']} ({p['difficulty']}, pattern: {p['pattern']})
{p['statement']}
Constraints: {'; '.join(p['constraints'])}
Expected optimal complexity (for your judgement only, do not volunteer it): time {p['complexity']['time']}, space {p['complexity']['space']}.
Candidate language: {lang}. Hints revealed so far: {ctx.hints_used} of {len(p['hints'])}.

CURRENT PHASE: {ctx.phase} ({PHASE_LABELS[ctx.phase]}). Phases in order: {', '.join(PHASES)}.
- clarify: let them restate the problem and ask questions; answer clarifications factually from the statement.
- approach: make them explain brute force and the better approach before coding; probe trade-offs.
- code: let them code; answer questions; do not review line by line unless asked.
- test: ask for edge cases and dry runs; use get_test_results to ground what you say.
- complexity: ask for time and space complexity with justification; push back on wrong answers.
- wrapup: thank them and tell them to click End interview.
Call set_phase when the current phase is clearly complete.

RULES:
1. Never write code, pseudo-code or a full algorithm. Never reveal hidden test inputs. Never say the expected complexity outright.
2. Ask one focused question at a time. Keep replies under 80 words. No praise inflation.
3. When they ask for help or seem stuck for 2+ turns, call give_hint and paraphrase the returned hint as a question or nudge.
4. Use get_test_results before commenting on correctness. Do not claim tests passed unless the tool says so.
5. You only see text, not the candidate's face or voice. Never comment on emotions or confidence.
"""


def _context_block(ctx: TurnContext) -> str:
    events = "\n".join(f"- {e}" for e in ctx.events) or "- none"
    return f"""[Live context, not from the candidate]
Recent events:
{events}
Current code ({ctx.language}):
<code>
{ctx.code[:6000]}
</code>"""


def llm_turn(
    ctx: TurnContext,
    candidate_text: str,
    key: str,
    chat_fn: Callable[..., dict[str, Any]] = llm.chat,
) -> TurnResult:
    msgs: list[dict[str, Any]] = [{"role": "system", "content": system_prompt(ctx)}]
    for m in ctx.history[-MAX_HISTORY:]:
        role = "assistant" if m["role"] == "interviewer" else "user"
        if m["role"] in ("interviewer", "candidate"):
            msgs.append({"role": role, "content": m["content"]})
    msgs.append({"role": "user", "content": f"{_context_block(ctx)}\n\n[Candidate]\n{candidate_text}"})

    phase, hints_used = ctx.phase, ctx.hints_used
    hint_text: str | None = None
    calls: list[dict[str, Any]] = []

    def handle(name: str, args: dict[str, Any]) -> str:
        nonlocal phase, hints_used, hint_text
        if name == "get_test_results":
            return json.dumps({"last_run": run_summary(ctx.last_run), "last_submit": run_summary(ctx.last_submit)})
        if name == "give_hint":
            if hints_used >= len(ctx.problem["hints"]):
                return json.dumps({"error": "All hints already revealed. Encourage the candidate to reason from them."})
            hint_text = ctx.problem["hints"][hints_used]
            hints_used += 1
            return json.dumps({"level": hints_used, "hint": hint_text})
        if name == "set_phase":
            phase = advance(phase, str(args.get("phase", "")))
            return json.dumps({"phase": phase})
        return json.dumps({"error": f"unknown tool {name}"})

    reply = ""
    for _ in range(MAX_TOOL_ROUNDS):
        message = chat_fn(msgs, key, tools=TOOLS)
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            reply = (message.get("content") or "").strip()
            break
        msgs.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": tool_calls})
        for tc in tool_calls:
            fn = tc.get("function", {})
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            out = handle(fn.get("name", ""), args)
            calls.append({"name": fn.get("name"), "args": args})
            msgs.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": out})
    if not reply:
        message = chat_fn(msgs, key)
        reply = (message.get("content") or "").strip()

    blocked = False
    if leaks_code(reply):
        blocked = True
        msgs.append({"role": "assistant", "content": reply})
        msgs.append({
            "role": "user",
            "content": "[System] Your last reply contained code, which is not allowed. Rewrite it as a short question or nudge with no code.",
        })
        retry = (chat_fn(msgs, key).get("content") or "").strip()
        reply = retry if retry and not leaks_code(retry) else (strip_code(retry or reply) or "Let's keep going. What would you try next, and why?")

    return TurnResult(reply or "Go on.", phase, hints_used, "llm", hint_text, calls, blocked)

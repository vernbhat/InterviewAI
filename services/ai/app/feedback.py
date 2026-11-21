"""Evidence-linked feedback reports. No overall score, no hiring recommendation.

Every observation carries evidence. Facts computed from submissions and the
transcript are marked ``source: "measured"``. LLM observations must quote the
candidate (or their code) verbatim; quotes that cannot be found are kept but
flagged ``verified: false`` so the UI can show them as "not verified".
"""

from __future__ import annotations

import re
import time
from typing import Any, Callable

from . import llm
from .interviewer import PHASES, stated_complexity


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def _complexity_class(s: str) -> str:
    m = re.search(r"O\s*\(\s*([^)]+)\)", s, re.I)
    if not m:
        return ""
    return re.sub(r"[\s*·]", "", m.group(1).lower()).replace("^", "")


def build_facts(session: dict[str, Any], problem: dict[str, Any], messages: list[dict[str, Any]], subs: list[dict[str, Any]]) -> dict[str, Any]:
    candidate = [m for m in messages if m["role"] == "candidate"]
    runs = [s for s in subs if s["kind"] == "run"]
    submits = [s for s in subs if s["kind"] == "submit"]
    final = submits[-1] if submits else None
    first_accept = next((i + 1 for i, s in enumerate(submits) if s["status"] == "accepted"), None)
    complexity_msgs = [m for m in candidate if stated_complexity(m["content"])]
    end = session.get("ended_at") or time.time()
    return {
        "problem": {"id": problem["id"], "title": problem["title"], "difficulty": problem["difficulty"]},
        "language": session["language"],
        "duration_min": round((end - session["created_at"]) / 60, 1),
        "hints_used": session["hints_used"],
        "hints_available": len(problem["hints"]),
        "runs": len(runs),
        "submits": len(submits),
        "final_submit": {"id": final["id"], "status": final["status"], "passed": final["passed"], "total": final["total"]} if final else None,
        "accepted_on_submit": first_accept,
        "phase_reached": session["phase"],
        "phases_completed": PHASES.index(session["phase"]),
        "candidate_messages": len(candidate),
        "candidate_words": sum(len(m["content"].split()) for m in candidate),
        "complexity_statement": {"message_id": complexity_msgs[-1]["id"], "quote": complexity_msgs[-1]["content"][:300]} if complexity_msgs else None,
        "expected_complexity": problem["complexity"],
        "mode": session["mode"],
    }


def measured_observations(facts: dict[str, Any]) -> list[dict[str, Any]]:
    obs: list[dict[str, Any]] = []

    def add(kind: str, category: str, text: str, evidence: dict[str, Any]) -> None:
        obs.append({"kind": kind, "category": category, "text": text, "evidence": evidence, "source": "measured", "verified": True})

    fs = facts["final_submit"]
    if fs is None:
        add("improvement", "Correctness", "You never submitted against the hidden tests, so correctness is unverified.", {"type": "metric", "submits": 0})
    elif fs["status"] == "accepted":
        attempt = facts["accepted_on_submit"]
        text = f"All {fs['total']} tests (including hidden ones) passed" + (" on the first submission." if attempt == 1 else f", after {attempt} submissions.")
        add("strength", "Correctness", text, {"type": "submission", "submission_id": fs["id"]})
    else:
        add("improvement", "Correctness", f"Final submission passed {fs['passed']} of {fs['total']} tests ({fs['status'].replace('_', ' ')}).", {"type": "submission", "submission_id": fs["id"]})

    if facts["submits"] and facts["runs"] == 0:
        add("improvement", "Testing", "You submitted without running the examples first.", {"type": "metric", "runs": 0})
    elif facts["submits"] > 2 and facts["accepted_on_submit"] != 1:
        add("improvement", "Testing", f"{facts['submits']} submissions suggests testing by trial and error. Dry-run edge cases before submitting.", {"type": "metric", "submits": facts["submits"]})

    cs = facts["complexity_statement"]
    exp_time = facts["expected_complexity"]["time"]
    if cs is None:
        add("improvement", "Complexity", f"You never stated the time or space complexity. Interviewers expect this (reference: {exp_time}).", {"type": "metric", "complexity_stated": False})
    else:
        stated, expected = _complexity_class(cs["quote"]), _complexity_class(exp_time)
        if stated and expected and stated == expected:
            add("strength", "Complexity", f"You stated a time complexity that matches the reference ({exp_time}).", {"type": "message", "message_id": cs["message_id"], "quote": cs["quote"]})
        else:
            obs.append({
                "kind": "note", "category": "Complexity",
                "text": f"You discussed complexity; compare your claim with the reference ({exp_time}). This check is a text heuristic.",
                "evidence": {"type": "message", "message_id": cs["message_id"], "quote": cs["quote"]},
                "source": "measured", "verified": False,
            })

    if facts["hints_used"] == 0:
        add("strength", "Independence", "You used no hints.", {"type": "metric", "hints_used": 0})
    else:
        add("note", "Independence", f"You used {facts['hints_used']} of {facts['hints_available']} hints.", {"type": "metric", "hints_used": facts["hints_used"]})

    if facts["candidate_messages"] < 3 or facts["candidate_words"] < 40:
        add("improvement", "Communication", f"You wrote {facts['candidate_words']} words across {facts['candidate_messages']} messages. Think aloud more; silence reads as being stuck.", {"type": "metric", "candidate_words": facts["candidate_words"]})
    return obs


FEEDBACK_PROMPT = """You are reviewing a mock coding interview transcript. Produce specific, evidence-based feedback.
Return JSON only:
{"summary": "<2 sentences>",
 "strengths": [{"point": "<what they did well>", "evidence": "<exact quote from the CANDIDATE's messages or code>"}],
 "improvements": [{"point": "<what to improve and how>", "evidence": "<exact quote from the CANDIDATE's messages or code>"}]}
Rules: 1-3 strengths and 1-3 improvements. Evidence must be copied verbatim (a short phrase is fine). Never invent quotes.
Do not give a score or hiring recommendation. Do not comment on emotions, confidence or tone of voice."""


def verify_quote(quote: str, candidate_messages: list[dict[str, Any]], code: str) -> dict[str, Any]:
    q = _norm(quote).strip("\"'. ")
    if len(q) < 4:
        return {"verified": False}
    for m in candidate_messages:
        if q in _norm(m["content"]):
            return {"verified": True, "message_id": m["id"]}
    if q in _norm(code):
        return {"verified": True, "in_code": True}
    return {"verified": False}


def llm_observations(
    facts: dict[str, Any], problem: dict[str, Any], messages: list[dict[str, Any]], code: str, key: str,
    chat_fn: Callable[..., dict[str, Any]] = llm.chat,
) -> tuple[str, list[dict[str, Any]]]:
    transcript = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages if m["role"] in ("candidate", "interviewer"))
    user = (
        f"Problem: {problem['title']} ({problem['difficulty']})\n{problem['statement']}\n\n"
        f"Measured facts: {facts}\n\nTranscript:\n{transcript[-12000:]}\n\nFinal code:\n{code[:6000]}"
    )
    message = chat_fn([{"role": "system", "content": FEEDBACK_PROMPT}, {"role": "user", "content": user}], key, json_mode=True, temperature=0.2, max_tokens=900)
    data = llm.parse_json(message.get("content") or "{}")
    candidate = [m for m in messages if m["role"] == "candidate"]
    obs = []
    for kind, items in (("strength", data.get("strengths") or []), ("improvement", data.get("improvements") or [])):
        for item in items[:3]:
            if not isinstance(item, dict) or not item.get("point"):
                continue
            quote = str(item.get("evidence") or "")
            check = verify_quote(quote, candidate, code)
            evidence = {"type": "quote", "quote": quote[:300]}
            if "message_id" in check:
                evidence["message_id"] = check["message_id"]
            if check.get("in_code"):
                evidence["type"] = "code"
            obs.append({"kind": kind, "category": "Interviewer notes", "text": str(item["point"])[:500], "evidence": evidence, "source": "llm", "verified": check["verified"]})
    return str(data.get("summary") or "")[:600], obs


def build_report(
    session: dict[str, Any], problem: dict[str, Any], messages: list[dict[str, Any]], subs: list[dict[str, Any]], key: str | None,
    chat_fn: Callable[..., dict[str, Any]] = llm.chat,
) -> dict[str, Any]:
    facts = build_facts(session, problem, messages, subs)
    observations = measured_observations(facts)
    summary, llm_error = "", None
    if key:
        try:
            summary, extra = llm_observations(facts, problem, messages, session["code"], key, chat_fn)
            observations += extra
        except llm.LLMError as exc:
            llm_error = str(exc)
    return {
        "session_id": session["id"],
        "generated_at": time.time(),
        "facts": facts,
        "summary": summary,
        "observations": observations,
        "llm_used": bool(key) and llm_error is None,
        "llm_error": llm_error,
        "disclaimer": "Practice feedback only. Measured items come from your submissions and transcript; interviewer notes are AI-generated and marked 'not verified' when their quoted evidence cannot be found.",
    }

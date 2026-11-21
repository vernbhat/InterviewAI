"""InterviewAI API (FastAPI)."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db, feedback, llm, runner
from .codegen import starter_code
from .interviewer import (
    PHASE_LABELS,
    PHASES,
    TurnContext,
    TurnResult,
    advance,
    llm_turn,
    offline_turn,
    opening_message,
    run_summary,
)
from .problems import all_problems, get_problem, public_view, summary

VERSION = "0.2.0"
app = FastAPI(title="InterviewAI API", version=VERSION)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

Language = Literal["cpp", "python"]
MAX_AUDIO_BYTES = 10 * 1024 * 1024


class CreateSession(BaseModel):
    problem_id: str
    language: Language = "cpp"


class CandidateMessage(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    code: str = Field(default="", max_length=64_000)


class RunRequest(BaseModel):
    code: str = Field(max_length=64_000)
    language: Language | None = None
    kind: Literal["run", "submit"] = "run"


class EndRequest(BaseModel):
    code: str | None = Field(default=None, max_length=64_000)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _session_or_404(sid: str) -> dict[str, Any]:
    s = db.get_session(sid)
    if not s:
        raise HTTPException(404, "Session not found")
    return s


def _active_or_409(sid: str) -> dict[str, Any]:
    s = _session_or_404(sid)
    if s["status"] != "active":
        raise HTTPException(409, "This interview has ended")
    return s


def _problem_or_404(pid: str) -> dict[str, Any]:
    p = get_problem(pid)
    if not p:
        raise HTTPException(404, "Problem not found")
    return p


def _last(subs: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    for s in reversed(subs):
        if s["kind"] == kind:
            return s["result"]
    return None


def _session_payload(s: dict[str, Any]) -> dict[str, Any]:
    return {**s, "phase_label": PHASE_LABELS[s["phase"]], "phase_index": PHASES.index(s["phase"])}


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": VERSION,
        "executor": runner.executor_name(),
        "server_llm_key": llm.server_key() is not None,
        "llm_model": llm.model(),
        "llm_provider": llm.provider(),
        "llm_base_url": llm.base_url() if llm.provider() == "openai" else None,
        "phases": [{"id": p, "label": PHASE_LABELS[p]} for p in PHASES],
    }


@app.get("/api/problems")
def list_problems() -> list[dict[str, Any]]:
    return [summary(p) for p in all_problems()]


@app.get("/api/problems/{problem_id}")
def problem_detail(problem_id: str) -> dict[str, Any]:
    return public_view(_problem_or_404(problem_id))


@app.post("/api/sessions", status_code=201)
def create_session(body: CreateSession, x_llm_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    problem = _problem_or_404(body.problem_id)
    mode = "llm" if llm.resolve_key(x_llm_api_key) else "offline"
    s = db.create_session(problem["id"], body.language, PHASES[0], mode, starter_code(problem, body.language))
    db.add_message(s["id"], "interviewer", opening_message(problem, mode), {"mode": mode, "phase": s["phase"]})
    return get_session_full(s["id"])


@app.get("/api/sessions")
def list_sessions() -> list[dict[str, Any]]:
    out = []
    for s in db.list_sessions():
        p = get_problem(s["problem_id"])
        out.append({**_session_payload(s), "problem_title": p["title"] if p else s["problem_id"], "difficulty": p["difficulty"] if p else None})
    return out


@app.get("/api/sessions/{sid}")
def get_session_full(sid: str) -> dict[str, Any]:
    s = _session_or_404(sid)
    subs = db.submissions(sid)
    return {
        "session": _session_payload(s),
        "problem": public_view(_problem_or_404(s["problem_id"])),
        "messages": db.messages(sid),
        "submissions": [{k: v for k, v in sub.items() if k != "code"} for sub in subs],
        "revealed_hints": _problem_or_404(s["problem_id"])["hints"][: s["hints_used"]],
        "report": db.get_report(sid),
    }


@app.delete("/api/sessions/{sid}", status_code=204)
def delete_session(sid: str) -> None:
    if not db.delete_session(sid):
        raise HTTPException(404, "Session not found")


def _context(s: dict[str, Any], problem: dict[str, Any], code: str) -> TurnContext:
    msgs = db.messages(s["id"])
    subs = db.submissions(s["id"])
    events = [m["content"] for m in msgs[-6:] if m["role"] == "system"]
    return TurnContext(
        problem=problem,
        language=s["language"],
        phase=s["phase"],
        hints_used=s["hints_used"],
        code=code,
        starter=starter_code(problem, s["language"]),
        history=msgs,
        last_run=_last(subs, "run"),
        last_submit=_last(subs, "submit"),
        events=events,
    )


@app.post("/api/sessions/{sid}/messages")
def send_message(sid: str, body: CandidateMessage, x_llm_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    s = _active_or_409(sid)
    problem = _problem_or_404(s["problem_id"])
    code = body.code or s["code"]
    ctx = _context(s, problem, code)
    db.add_message(sid, "candidate", body.text.strip())
    key = llm.resolve_key(x_llm_api_key)

    result: TurnResult
    if key:
        try:
            result = llm_turn(ctx, body.text.strip(), key)
        except llm.LLMError as exc:
            result = offline_turn(ctx, body.text.strip())
            result.error = str(exc)
    else:
        result = offline_turn(ctx, body.text.strip())

    meta: dict[str, Any] = {"mode": result.mode, "phase": result.phase}
    if result.tool_calls:
        meta["tool_calls"] = result.tool_calls
    if result.leak_blocked:
        meta["leak_blocked"] = True
    if result.error:
        meta["fallback_error"] = result.error
    if result.hint_text:
        meta["hint_level"] = result.hints_used
        db.add_message(sid, "hint", result.hint_text, {"level": result.hints_used, "by": "interviewer"})
    reply = db.add_message(sid, "interviewer", result.reply, meta)
    db.update_session(sid, phase=result.phase, hints_used=result.hints_used, code=code)
    return {"reply": reply, "session": _session_payload(_session_or_404(sid)), "hint": result.hint_text}


@app.post("/api/sessions/{sid}/hint")
def request_hint(sid: str) -> dict[str, Any]:
    s = _active_or_409(sid)
    problem = _problem_or_404(s["problem_id"])
    if s["hints_used"] >= len(problem["hints"]):
        raise HTTPException(409, "All hints have been revealed")
    level = s["hints_used"] + 1
    text = problem["hints"][level - 1]
    msg = db.add_message(sid, "hint", text, {"level": level, "by": "candidate"})
    db.update_session(sid, hints_used=level)
    return {"hint": msg, "level": level, "remaining": len(problem["hints"]) - level}


@app.post("/api/sessions/{sid}/run")
def run_code(sid: str, body: RunRequest) -> dict[str, Any]:
    s = _active_or_409(sid)
    problem = _problem_or_404(s["problem_id"])
    language = body.language or s["language"]
    report = runner.grade(problem, language, body.code, include_hidden=body.kind == "submit").public()
    sub_id = db.add_submission(sid, body.kind, language, body.code, report)

    phase = s["phase"]
    phase = advance(phase, "code")
    if body.kind == "submit" and report["status"] == "accepted":
        phase = advance(phase, "test")
    label = "Submit" if body.kind == "submit" else "Run"
    db.add_message(sid, "system", f"{label} #{sub_id}: {report['status'].replace('_', ' ')} ({report['passed']}/{report['total']} tests)", {"submission_id": sub_id})
    db.update_session(sid, phase=phase, code=body.code, language=language)
    return {"submission_id": sub_id, "result": report, "session": _session_payload(_session_or_404(sid))}


@app.post("/api/sessions/{sid}/end")
def end_session(sid: str, body: EndRequest, x_llm_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    s = _session_or_404(sid)
    if s["status"] == "active":
        fields: dict[str, Any] = {"status": "ended", "ended_at": time.time()}
        if body.code is not None:
            fields["code"] = body.code
        db.update_session(sid, **fields)
        s = _session_or_404(sid)
    existing = db.get_report(sid)
    if existing:
        return existing
    problem = _problem_or_404(s["problem_id"])
    report = feedback.build_report(s, problem, db.messages(sid), db.submissions(sid), llm.resolve_key(x_llm_api_key))
    db.save_report(sid, report)
    return report


@app.post("/api/speech/transcribe")
async def transcribe(file: UploadFile = File(...), x_llm_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    key = (x_llm_api_key or "").strip() or (llm.server_key() if llm.provider() == "openai" else None)
    if not key:
        raise HTTPException(503, "Voice input needs a Groq API key (Whisper). Add one in Settings.")
    audio = await file.read()
    if not audio:
        raise HTTPException(400, "Empty audio")
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio clip too large (max 10 MB)")
    try:
        text = llm.transcribe(audio, file.filename or "audio.webm", file.content_type or "audio/webm", key)
    except llm.LLMError as exc:
        raise HTTPException(502, str(exc)) from exc
    return {"text": text}


@app.get("/api/sessions/{sid}/debug/context")
def debug_context(sid: str) -> dict[str, Any]:
    """What the interviewer sees (minus the system prompt). Useful when tuning prompts."""
    s = _session_or_404(sid)
    subs = db.submissions(sid)
    return {"phase": s["phase"], "last_run": run_summary(_last(subs, "run")), "last_submit": run_summary(_last(subs, "submit"))}


# Serve the built frontend in production (single service deploy).
STATIC_DIR = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parents[3] / "apps" / "web" / "dist"))
if (STATIC_DIR / "index.html").is_file() and (STATIC_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        target = STATIC_DIR / path
        if path and target.is_file() and STATIC_DIR in target.resolve().parents:
            return FileResponse(target)
        return FileResponse(STATIC_DIR / "index.html")

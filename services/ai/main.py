from typing import Any, Literal

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="Interview AI Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InterviewTurnRequest(BaseModel):
    session_id: str
    role_title: str = "Backend Engineer"
    difficulty: Literal["junior", "mid", "senior", "staff"] = "senior"
    transcript: list[dict[str, str]] = Field(default_factory=list)
    code: str = ""


class HintRequest(BaseModel):
    session_id: str
    problem: str
    code: str
    language: str = "typescript"


class EmotionRequest(BaseModel):
    session_id: str
    transcript: str = ""
    face_signals: dict[str, Any] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    session_id: str
    transcript: list[dict[str, str]] = Field(default_factory=list)
    code: str
    tests_passed: int = 0
    tests_total: int = 0
    signal_summary: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/interviewer/turn")
def interviewer_turn(request: InterviewTurnRequest) -> dict[str, Any]:
    latest = request.transcript[-1]["text"] if request.transcript else ""
    prompt = "Can you explain the time complexity and the edge cases you are guarding against?"
    if "stuck" in latest.lower() or len(request.code.strip()) < 80:
        prompt = "Talk me through your current approach before we optimize it."

    return {
        "message": prompt,
        "intent": "probe_reasoning",
        "rubric_focus": ["problem decomposition", "complexity analysis", "communication"],
    }


@app.post("/hint")
def hint(request: HintRequest) -> dict[str, Any]:
    code = request.code.lower()
    if "map" not in code and "dict" not in code:
        nudge = "Consider whether a hash map can preserve what you have already seen."
    elif "return" not in code:
        nudge = "You are close. Define the exact value you want to return for success and failure."
    else:
        nudge = "Add one focused test for a duplicate-heavy input before changing the algorithm."

    return {
        "hint": nudge,
        "level": "nudge",
        "follow_up": "What invariant stays true after each iteration?",
    }


@app.post("/speech/transcribe")
async def transcribe(file: UploadFile) -> dict[str, Any]:
    # Wire this to Whisper once model files or hosted inference are available.
    return {
        "filename": file.filename,
        "text": "Transcription placeholder. Connect Whisper in services/ai/main.py.",
        "confidence": 0.0,
    }


@app.post("/emotion/analyze")
def analyze_emotion(request: EmotionRequest) -> dict[str, Any]:
    lower = request.transcript.lower()
    stress = 0.68 if any(word in lower for word in ["sorry", "confused", "stuck"]) else 0.28
    engagement = 0.82 if len(request.transcript) > 40 else 0.55

    return {
        "sentiment": "focused" if stress < 0.5 else "strained",
        "engagement": engagement,
        "stress": stress,
        "notes": ["Use as an interviewer signal, not as a hiring decision by itself."],
    }


@app.post("/feedback/generate")
def generate_feedback(request: FeedbackRequest) -> dict[str, Any]:
    pass_rate = request.tests_passed / request.tests_total if request.tests_total else 0
    communication_score = min(1.0, max(0.35, len(request.transcript) / 12))
    overall = round((pass_rate * 0.55 + communication_score * 0.25 + 0.2) * 100, 1)

    return {
        "overall_score": overall,
        "strengths": [
            "Maintained a clear implementation path",
            "Responded well to interviewer nudges",
        ],
        "improvements": [
            "State complexity before coding the final solution",
            "Add edge-case tests earlier in the session",
        ],
        "recommendation": "advance" if overall >= 72 else "needs_follow_up",
        "rubric": {
            "problem_solving": round(pass_rate * 100, 1),
            "communication": round(communication_score * 100, 1),
            "code_quality": 76,
        },
    }

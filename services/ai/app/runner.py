"""Code execution: a local subprocess executor for development and a Judge0 executor.

Select with EXECUTOR=local|judge0 (default: local).

The local executor applies CPU, memory and output limits with setrlimit and runs
in a throwaway temp dir, but it is NOT a security sandbox: it has the same
network and filesystem access as the API process. Use Judge0 for anything
exposed to other people.
"""

from __future__ import annotations

import base64
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from .codegen import build_program, parse_output

COMPILE_TIMEOUT_S = 20
RUN_TIMEOUT_S = float(os.getenv("RUN_TIMEOUT_S", "5"))
MEMORY_LIMIT_MB = int(os.getenv("RUN_MEMORY_MB", "512"))
MAX_OUTPUT_BYTES = 256 * 1024
MAX_CODE_BYTES = 64 * 1024


@dataclass
class RawResult:
    status: str  # ok | compile_error | runtime_error | timeout | internal_error
    stdout: str = ""
    stderr: str = ""
    compile_output: str = ""
    elapsed_ms: int = 0


@dataclass
class TestOutcome:
    index: int
    hidden: bool
    passed: bool
    status: str  # passed | wrong_answer | error | not_run
    args: Any = None
    expected: Any = None
    actual: Any = None
    error: str | None = None

    def public(self) -> dict[str, Any]:
        item: dict[str, Any] = {"index": self.index, "hidden": self.hidden, "passed": self.passed, "status": self.status}
        if not self.hidden:
            item.update(args=self.args, expected=self.expected, actual=self.actual, error=self.error)
        return item


@dataclass
class RunReport:
    status: str  # accepted | wrong_answer | compile_error | runtime_error | timeout | internal_error
    passed: int
    total: int
    elapsed_ms: int
    tests: list[TestOutcome] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    compile_output: str = ""
    executor: str = "local"

    def public(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "passed": self.passed,
            "total": self.total,
            "elapsed_ms": self.elapsed_ms,
            "tests": [t.public() for t in self.tests],
            "stdout": self.stdout[:8000],
            "stderr": self.stderr[:8000],
            "compile_output": self.compile_output[:8000],
            "executor": self.executor,
        }


# --------------------------------------------------------------------------- #
# Executors
# --------------------------------------------------------------------------- #

def _limits() -> None:  # pragma: no cover - runs in the child process
    import resource

    cpu = int(RUN_TIMEOUT_S) + 1
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    mem = MEMORY_LIMIT_MB * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES * 4, MAX_OUTPUT_BYTES * 4))
    os.setsid()


def _run(cmd: list[str], cwd: str, timeout: float, limit: bool) -> tuple[int | None, str, str, int]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            preexec_fn=_limits if limit and os.name == "posix" else None,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8"},
        )
        code: int | None = proc.returncode
        out, err = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        code = None
        out, err = exc.stdout or b"", exc.stderr or b""
    elapsed = int((time.perf_counter() - start) * 1000)
    return code, out[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"), err[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"), elapsed


def run_local(language: str, source: str) -> RawResult:
    workdir = tempfile.mkdtemp(prefix="iv-run-")
    try:
        if language == "cpp":
            compiler = os.getenv("CXX", "g++")
            if not shutil.which(compiler):
                return RawResult("internal_error", stderr=f"{compiler} not found on PATH")
            src = os.path.join(workdir, "main.cpp")
            with open(src, "w") as fh:
                fh.write(source)
            code, out, err, _ = _run([compiler, "-std=c++17", "-O2", "-pipe", "-o", "main", "main.cpp"], workdir, COMPILE_TIMEOUT_S, False)
            if code != 0:
                return RawResult("compile_error", compile_output=(err or out or "compilation timed out").strip())
            cmd = ["./main"]
        elif language == "python":
            with open(os.path.join(workdir, "main.py"), "w") as fh:
                fh.write(source)
            cmd = [os.getenv("PYTHON_BIN", sys.executable), "-I", "main.py"]
        else:
            return RawResult("internal_error", stderr=f"unsupported language {language}")

        code, out, err, elapsed = _run(cmd, workdir, RUN_TIMEOUT_S, True)
        if code is None or code in (-9, -24, 137, 152):
            status = "timeout"
        elif code != 0:
            status = "runtime_error"
        else:
            status = "ok"
        if language == "python" and status == "runtime_error" and ("SyntaxError" in err or "IndentationError" in err):
            return RawResult("compile_error", compile_output=err.strip(), elapsed_ms=elapsed)
        return RawResult(status, stdout=out, stderr=err, elapsed_ms=elapsed)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


JUDGE0_LANGUAGE_IDS = {
    "cpp": int(os.getenv("JUDGE0_CPP_ID", "54")),  # C++ (GCC 9.2.0) on Judge0 CE
    "python": int(os.getenv("JUDGE0_PYTHON_ID", "71")),  # Python 3.8.1 on Judge0 CE
}


def run_judge0(language: str, source: str) -> RawResult:
    base = os.getenv("JUDGE0_URL", "http://localhost:2358").rstrip("/")
    headers = {"Content-Type": "application/json"}
    if os.getenv("JUDGE0_RAPIDAPI_KEY"):
        headers["X-RapidAPI-Key"] = os.environ["JUDGE0_RAPIDAPI_KEY"]
        headers["X-RapidAPI-Host"] = os.getenv("JUDGE0_RAPIDAPI_HOST", "judge0-ce.p.rapidapi.com")
    if os.getenv("JUDGE0_AUTH_TOKEN"):
        headers["X-Auth-Token"] = os.environ["JUDGE0_AUTH_TOKEN"]
    body = {
        "language_id": JUDGE0_LANGUAGE_IDS[language],
        "source_code": base64.b64encode(source.encode()).decode(),
        "cpu_time_limit": RUN_TIMEOUT_S,
        "memory_limit": MEMORY_LIMIT_MB * 1024,
    }
    try:
        resp = httpx.post(f"{base}/submissions?base64_encoded=true&wait=true", json=body, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        return RawResult("internal_error", stderr=f"Judge0 request failed: {exc}")

    def dec(key: str) -> str:
        val = data.get(key)
        return base64.b64decode(val).decode("utf-8", "replace") if val else ""

    status_id = (data.get("status") or {}).get("id", 13)
    elapsed = int(float(data.get("time") or 0) * 1000)
    if status_id == 6:
        return RawResult("compile_error", compile_output=dec("compile_output"))
    if status_id == 5:
        return RawResult("timeout", stdout=dec("stdout"), stderr=dec("stderr"), elapsed_ms=elapsed)
    if status_id in (3, 4):  # accepted / wrong answer (no expected_output given, so 3 is normal)
        return RawResult("ok", stdout=dec("stdout"), stderr=dec("stderr"), elapsed_ms=elapsed)
    if 7 <= status_id <= 12:
        return RawResult("runtime_error", stdout=dec("stdout"), stderr=dec("stderr") or data.get("message") or "", elapsed_ms=elapsed)
    return RawResult("internal_error", stderr=f"Judge0 status {status_id}: {data.get('message')}")


def executor_name() -> str:
    return "judge0" if os.getenv("EXECUTOR", "local").lower() == "judge0" else "local"


# --------------------------------------------------------------------------- #
# Grading
# --------------------------------------------------------------------------- #

def _normalise(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def grade(problem: dict[str, Any], language: str, code: str, include_hidden: bool) -> RunReport:
    if len(code.encode()) > MAX_CODE_BYTES:
        return RunReport("internal_error", 0, 0, 0, stderr="Code is larger than 64 KB.")
    tests = [t for t in problem["tests"] if include_hidden or not t["hidden"]]
    mark = f"@@IV-{secrets.token_hex(6)}@@"
    source = build_program(problem, language, code, tests, mark)
    backend = executor_name()
    raw = run_judge0(language, source) if backend == "judge0" else run_local(language, source)

    if raw.status in ("compile_error", "internal_error"):
        outcomes = [TestOutcome(i, t["hidden"], False, "not_run", t["args"], t["expected"]) for i, t in enumerate(tests)]
        return RunReport(raw.status, 0, len(tests), raw.elapsed_ms, outcomes, compile_output=raw.compile_output, stderr=raw.stderr, executor=backend)

    parsed, candidate_stdout = parse_output(raw.stdout, len(tests), mark)
    outcomes = []
    for i, t in enumerate(tests):
        if i not in parsed:
            outcomes.append(TestOutcome(i, t["hidden"], False, "not_run", t["args"], t["expected"]))
            continue
        state, value = parsed[i]
        if state == "err":
            outcomes.append(TestOutcome(i, t["hidden"], False, "error", t["args"], t["expected"], None, str(value)))
            continue
        ok = _normalise(value) == _normalise(t["expected"])
        outcomes.append(TestOutcome(i, t["hidden"], ok, "passed" if ok else "wrong_answer", t["args"], t["expected"], value))

    passed = sum(o.passed for o in outcomes)
    if raw.status == "timeout":
        status = "timeout"
    elif raw.status == "runtime_error" or any(o.status == "error" for o in outcomes):
        status = "runtime_error"
    elif passed == len(tests):
        status = "accepted"
    else:
        status = "wrong_answer"
    return RunReport(status, passed, len(tests), raw.elapsed_ms, outcomes, candidate_stdout, raw.stderr, executor=backend)

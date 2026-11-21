import { CheckCircle2, CircleSlash, XCircle } from "lucide-react";
import { formatValue, RunResult } from "../api";

const statusText: Record<RunResult["status"], string> = {
  accepted: "Accepted",
  wrong_answer: "Wrong answer",
  compile_error: "Compile error",
  runtime_error: "Runtime error",
  timeout: "Time limit exceeded",
  internal_error: "Runner error"
};

export function TestResults({ result, kind }: { result: RunResult | null; kind: "run" | "submit" | null }) {
  if (!result) return <p className="muted small pad">Run executes the visible examples. Submit runs every test, including hidden ones.</p>;
  const visible = result.tests.filter((t) => !t.hidden);
  const hidden = result.tests.filter((t) => t.hidden);
  return (
    <div className="results">
      <div className={`result-head ${result.status === "accepted" ? "ok" : "bad"}`}>
        <strong>{statusText[result.status]}</strong>
        <span>
          {result.passed}/{result.total} {kind === "submit" ? "tests (incl. hidden)" : "examples"} · {result.elapsed_ms} ms
        </span>
      </div>
      {(result.compile_output || (result.status === "internal_error" && result.stderr)) && <pre className="console error">{result.compile_output || result.stderr}</pre>}
      {visible.map((t) => (
        <div key={t.index} className="test">
          <div className="test-title">
            {t.passed ? <CheckCircle2 size={14} className="ok" /> : t.status === "not_run" ? <CircleSlash size={14} /> : <XCircle size={14} className="bad" />}
            Example {t.index + 1}
            <span className="muted small">{t.status.replace("_", " ")}</span>
          </div>
          {!t.passed && t.status !== "not_run" && (
            <dl className="kv mono small">
              <dt>Input</dt>
              <dd>{(t.args ?? []).map(formatValue).join(", ")}</dd>
              <dt>Expected</dt>
              <dd>{formatValue(t.expected)}</dd>
              <dt>{t.error ? "Error" : "Got"}</dt>
              <dd>{t.error ?? formatValue(t.actual)}</dd>
            </dl>
          )}
        </div>
      ))}
      {hidden.length > 0 && (
        <div className="hidden-grid" aria-label="Hidden tests">
          <span className="muted small">Hidden tests</span>
          {hidden.map((t) => (
            <span key={t.index} className={`dot ${t.passed ? "ok" : "bad"}`} title={t.passed ? "passed" : t.status.replace("_", " ")} />
          ))}
        </div>
      )}
      {result.stdout && (
        <>
          <div className="muted small pad-top">Your stdout</div>
          <pre className="console">{result.stdout}</pre>
        </>
      )}
      {result.status === "runtime_error" && result.stderr && <pre className="console error">{result.stderr.slice(-2000)}</pre>}
    </div>
  );
}

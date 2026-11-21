import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, CircleAlert, Info, RotateCcw } from "lucide-react";
import { api, languageLabel, Observation, SessionFull } from "../api";
import { navigate } from "../App";
import { Paragraphs } from "../components/Markdown";

const phaseLabel = { clarify: "Clarify", approach: "Approach", code: "Code", test: "Test", complexity: "Complexity", wrapup: "Wrap up" } as const;
const kindIcon = { strength: CheckCircle2, improvement: CircleAlert, note: Info };
const kindTitle = { strength: "What went well", improvement: "What to work on", note: "Notes" };

function Badge({ o }: { o: Observation }) {
  if (o.source === "measured") return <span className={`badge ${o.verified ? "measured" : "unverified"}`}>{o.verified ? "Measured" : "Heuristic"}</span>;
  return <span className={`badge ${o.verified ? "verified" : "unverified"}`}>{o.verified ? "AI note · quote verified" : "AI note · not verified"}</span>;
}

export function ReportPage({ id }: { id: string }) {
  const [data, setData] = useState<SessionFull | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        let d = await api.session(id);
        if (!d.report) {
          await api.end(id, d.session.code);
          d = await api.session(id);
        }
        setData(d);
      } catch (e) {
        setError((e as Error).message);
      }
    })();
  }, [id]);

  if (error) return <div className="banner error">{error}</div>;
  if (!data || !data.report) return <p className="muted">Building your report...</p>;
  const { report, problem, session } = data;
  const f = report.facts;
  const groups = (["strength", "improvement", "note"] as const).map((k) => [k, report.observations.filter((o) => o.kind === k)] as const);

  return (
    <div className="report">
      <div className="row between wrap">
        <button className="ghost" onClick={() => navigate("/history")}>
          <ArrowLeft size={16} aria-hidden /> History
        </button>
        <button onClick={async () => navigate(`/interview/${(await api.createSession(problem.id, session.language)).session.id}`)}>
          <RotateCcw size={16} aria-hidden /> Try this problem again
        </button>
      </div>
      <h1>
        {problem.title} <span className={`pill ${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span>
      </h1>
      <p className="muted">
        {languageLabel[f.language]} · {f.duration_min} min · {new Date(session.created_at * 1000).toLocaleString()} · {f.mode === "llm" ? "AI interviewer" : "offline script"}
      </p>

      <div className="stats">
        <div className="stat">
          <span className="label">Tests on final submit</span>
          <span className="value">{f.final_submit ? `${f.final_submit.passed}/${f.final_submit.total}` : "not submitted"}</span>
        </div>
        <div className="stat">
          <span className="label">Hints used</span>
          <span className="value">
            {f.hints_used}/{f.hints_available}
          </span>
        </div>
        <div className="stat">
          <span className="label">Runs / submits</span>
          <span className="value">
            {f.runs} / {f.submits}
          </span>
        </div>
        <div className="stat">
          <span className="label">Reached phase</span>
          <span className="value">{phaseLabel[f.phase_reached]}</span>
        </div>
        <div className="stat">
          <span className="label">Reference complexity</span>
          <span className="value small">{f.expected_complexity.time}</span>
        </div>
      </div>

      {report.summary && (
        <section className="card">
          <Paragraphs text={report.summary} />
        </section>
      )}
      {report.llm_error && <div className="banner info">AI notes unavailable: {report.llm_error}. Measured facts are still shown.</div>}

      {groups.map(([kind, items]) => {
        if (!items.length) return null;
        const Icon = kindIcon[kind];
        return (
          <section key={kind} className="card">
            <h2 className="row gap">
              <Icon size={18} aria-hidden className={kind === "strength" ? "ok" : kind === "improvement" ? "warn" : "muted"} /> {kindTitle[kind]}
            </h2>
            <ul className="observations">
              {items.map((o, i) => (
                <li key={i}>
                  <div className="row between gap wrap">
                    <strong>{o.category}</strong>
                    <Badge o={o} />
                  </div>
                  <p>{o.text}</p>
                  {o.evidence.quote && <blockquote>"{o.evidence.quote}"</blockquote>}
                  {o.evidence.submission_id !== undefined && <span className="small muted">Evidence: submission #{o.evidence.submission_id}</span>}
                </li>
              ))}
            </ul>
          </section>
        );
      })}

      <details className="card">
        <summary>Transcript ({data.messages.filter((m) => m.role !== "system").length} messages)</summary>
        <div className="chat static">
          {data.messages.map((m) => (
            <div key={m.id} className={`msg ${m.role}`}>
              {m.role === "system" ? <div className="small muted">{m.content}</div> : <Paragraphs text={m.content} />}
            </div>
          ))}
        </div>
      </details>
      <p className="small muted">{report.disclaimer}</p>
    </div>
  );
}

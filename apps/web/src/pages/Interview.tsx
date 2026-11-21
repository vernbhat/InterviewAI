import { FormEvent, lazy, Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Flag, Lightbulb, Play, RotateCcw, Send, UploadCloud } from "lucide-react";
import { api, formatValue, Language, languageLabel, Message, RunResult, SessionFull, settings } from "../api";
import { navigate } from "../App";
import { Inline, Paragraphs } from "../components/Markdown";
import { PhaseBar } from "../components/PhaseBar";
import { PushToTalk } from "../components/PushToTalk";
import { TestResults } from "../components/TestResults";

const CodeEditor = lazy(() => import("../components/CodeEditor").then((m) => ({ default: m.CodeEditor })));

const codeKey = (id: string, lang: Language) => `interviewai.code.${id}.${lang}`;

function useElapsed(since: number | undefined, until: number | null | undefined) {
  const [now, setNow] = useState(Date.now() / 1000);
  useEffect(() => {
    if (until) return;
    const t = setInterval(() => setNow(Date.now() / 1000), 1000);
    return () => clearInterval(t);
  }, [until]);
  if (!since) return "0:00";
  const s = Math.max(0, Math.floor((until ?? now) - since));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export function Interview({ id }: { id: string }) {
  const [data, setData] = useState<SessionFull | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<Language>("cpp");
  const [code, setCode] = useState("");
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState<null | "send" | "run" | "submit" | "hint" | "end">(null);
  const [result, setResult] = useState<{ kind: "run" | "submit"; result: RunResult } | null>(null);
  const chatEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.session(id).then(
      (d) => {
        if (d.session.status === "ended") {
          navigate(`/report/${id}`);
          return;
        }
        setData(d);
        const lang = d.session.language;
        setLanguage(lang);
        setCode(localStorage.getItem(codeKey(id, lang)) ?? d.session.code ?? d.problem.starter_code[lang]);
        const last = [...d.submissions].reverse()[0];
        if (last) setResult({ kind: last.kind, result: last.result });
      },
      (e: Error) => setError(e.message)
    );
  }, [id]);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [data?.messages.length]);

  const elapsed = useElapsed(data?.session.created_at, data?.session.ended_at);

  const updateCode = useCallback(
    (v: string) => {
      setCode(v);
      localStorage.setItem(codeKey(id, language), v);
    },
    [id, language]
  );

  function switchLanguage(next: Language) {
    if (!data || next === language) return;
    localStorage.setItem(codeKey(id, language), code);
    setLanguage(next);
    setCode(localStorage.getItem(codeKey(id, next)) ?? data.problem.starter_code[next]);
  }

  function appendMessages(...msgs: Message[]) {
    setData((d) => (d ? { ...d, messages: [...d.messages, ...msgs] } : d));
  }

  async function send(e?: FormEvent) {
    e?.preventDefault();
    const text = draft.trim();
    if (!text || !data || busy) return;
    setBusy("send");
    setError(null);
    const optimistic: Message = { id: -Date.now(), role: "candidate", content: text, meta: {}, created_at: Date.now() / 1000 };
    appendMessages(optimistic);
    setDraft("");
    try {
      const r = await api.send(id, text, code);
      const fresh = await api.session(id);
      setData(fresh);
      if (r.reply.meta.fallback_error) setError(`AI interviewer unavailable, used offline script: ${String(r.reply.meta.fallback_error)}`);
    } catch (err) {
      setError((err as Error).message);
      setDraft(text);
      setData((d) => (d ? { ...d, messages: d.messages.filter((m) => m.id !== optimistic.id) } : d));
    } finally {
      setBusy(null);
    }
  }

  async function run(kind: "run" | "submit") {
    if (!data || busy) return;
    setBusy(kind);
    setError(null);
    try {
      const r = await api.run(id, code, language, kind);
      setResult({ kind, result: r.result });
      setData(await api.session(id));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function hint() {
    if (!data || busy) return;
    setBusy("hint");
    try {
      await api.hint(id);
      setData(await api.session(id));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function end() {
    if (!data || busy) return;
    if (!window.confirm("End the interview and generate your report?")) return;
    setBusy("end");
    try {
      await api.end(id, code);
      navigate(`/report/${id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(null);
    }
  }

  if (!data) return <div className="pad">{error ? <div className="banner error">{error}</div> : <p className="muted">Loading interview...</p>}</div>;

  const { problem, session } = data;
  const hintsLeft = problem.hint_count - session.hints_used;
  const voiceEnabled = Boolean(settings.getKey()) || session.mode === "llm";

  return (
    <div className="interview">
      <div className="interview-head">
        <div className="row gap">
          <h1 className="h-problem">{problem.title}</h1>
          <span className={`pill ${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span>
          <span className={`pill ${session.mode === "llm" ? "llm" : "offline"}`}>{session.mode === "llm" ? "AI interviewer" : "Offline script"}</span>
        </div>
        <PhaseBar current={session.phase} />
        <div className="row gap">
          <span className="timer mono" aria-label="Elapsed time">{elapsed}</span>
          <button className="danger" onClick={end} disabled={busy !== null}>
            <Flag size={16} aria-hidden /> {busy === "end" ? "Generating report..." : "End interview"}
          </button>
        </div>
      </div>
      {error && <div className="banner error slim">{error}</div>}

      <div className="panes">
        <section className="pane problem-pane" aria-label="Problem">
          <div className="prose">
            <Paragraphs text={problem.statement} />
            <h3>Examples</h3>
            {problem.examples.map((ex, i) => (
              <div key={i} className="example">
                <div className="mono small">
                  <span className="muted">Input: </span>
                  {problem.function.params.map((p, j) => `${p.name} = ${formatValue(ex.args[j])}`).join(", ")}
                </div>
                <div className="mono small">
                  <span className="muted">Output: </span>
                  {formatValue(ex.expected)}
                </div>
                {ex.explanation && <div className="small muted">{ex.explanation}</div>}
              </div>
            ))}
            <h3>Constraints</h3>
            <ul className="small">
              {problem.constraints.map((c) => (
                <li key={c}>
                  <Inline text={c} />
                </li>
              ))}
            </ul>
            <p className="small muted">{problem.hidden_test_count} hidden tests run on Submit.</p>
            {data.revealed_hints.length > 0 && (
              <>
                <h3>Hints used</h3>
                <ol className="hints small">
                  {data.revealed_hints.map((h) => (
                    <li key={h}>{h}</li>
                  ))}
                </ol>
              </>
            )}
          </div>
        </section>

        <section className="pane editor-pane" aria-label="Code editor">
          <div className="toolbar">
            <div className="segmented small" role="radiogroup" aria-label="Language">
              {(Object.keys(languageLabel) as Language[]).map((l) => (
                <button key={l} role="radio" aria-checked={language === l} className={language === l ? "on" : ""} onClick={() => switchLanguage(l)}>
                  {languageLabel[l]}
                </button>
              ))}
            </div>
            <div className="row gap">
              <button
                className="ghost"
                title="Reset to starter code"
                onClick={() => window.confirm("Replace your code with the starter template?") && updateCode(problem.starter_code[language])}
              >
                <RotateCcw size={15} aria-hidden /> Reset
              </button>
              <button onClick={() => run("run")} disabled={busy !== null} title="Ctrl/Cmd + Enter">
                <Play size={15} aria-hidden /> {busy === "run" ? "Running..." : "Run"}
              </button>
              <button className="primary" onClick={() => run("submit")} disabled={busy !== null}>
                <UploadCloud size={15} aria-hidden /> {busy === "submit" ? "Judging..." : "Submit"}
              </button>
            </div>
          </div>
          <div className="editor-wrap">
            <Suspense fallback={<p className="muted pad">Loading editor...</p>}>
              <CodeEditor language={language} value={code} onChange={updateCode} onRun={() => run("run")} />
            </Suspense>
          </div>
          <div className="results-wrap">
            <TestResults result={result?.result ?? null} kind={result?.kind ?? null} />
          </div>
        </section>

        <section className="pane chat-pane" aria-label="Interviewer chat">
          <div className="chat" aria-live="polite">
            {data.messages.map((m) => (
              <div key={m.id} className={`msg ${m.role}`}>
                {m.role === "interviewer" && <div className="who">Interviewer</div>}
                {m.role === "hint" && <div className="who">Hint {String(m.meta.level ?? "")}</div>}
                {m.role === "system" ? <div className="small muted">{m.content}</div> : <Paragraphs text={m.content} />}
              </div>
            ))}
            {busy === "send" && <div className="msg interviewer typing">Interviewer is thinking...</div>}
            <div ref={chatEnd} />
          </div>
          <form className="composer" onSubmit={send}>
            <textarea
              aria-label="Your reply"
              placeholder="Explain your thinking, ask a question..."
              value={draft}
              rows={3}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
            />
            <div className="row between">
              <button type="button" className="ghost" onClick={hint} disabled={hintsLeft <= 0 || busy !== null}>
                <Lightbulb size={15} aria-hidden /> Hint ({hintsLeft} left)
              </button>
              <div className="row gap">
                <PushToTalk enabled={voiceEnabled} onText={(t) => setDraft((d) => (d ? `${d} ${t}` : t))} onError={setError} />
                <button className="primary" type="submit" disabled={!draft.trim() || busy !== null}>
                  <Send size={15} aria-hidden /> Send
                </button>
              </div>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}

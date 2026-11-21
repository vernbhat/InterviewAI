import { useEffect, useMemo, useState } from "react";
import { Play, Search, Shuffle } from "lucide-react";
import { api, Language, languageLabel, ProblemSummary } from "../api";
import { navigate } from "../App";
import { store } from "../storage";

const difficulties = ["All", "Easy", "Medium", "Hard"] as const;
const rank: Record<string, number> = { Easy: 0, Medium: 1, Hard: 2 };

export function Home({ llmReady, onOpenSettings }: { llmReady: boolean; onOpenSettings: () => void }) {
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [filter, setFilter] = useState<(typeof difficulties)[number]>("All");
  const [selected, setSelected] = useState<string | null>(null);
  const [language, setLanguage] = useState<Language>(() => (store.get("interviewai.lang") as Language) || "cpp");
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api.problems().then(
      (p) => {
        setProblems(p);
        setSelected((s) => s ?? p[0]?.id ?? null);
      },
      (e: Error) => setError(e.message)
    );
  }, []);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    return problems
      .map((p, i) => ({ p, i }))
      .filter(({ p }) => (filter === "All" || p.difficulty === filter) && (!q || p.title.toLowerCase().includes(q) || p.pattern.toLowerCase().includes(q)))
      .sort((a, b) => rank[a.p.difficulty] - rank[b.p.difficulty] || a.i - b.i)
      .map(({ p }) => p);
  }, [problems, filter, query]);

  function surprise() {
    if (!shown.length) return;
    const pick = shown[Math.floor(Math.random() * shown.length)];
    setSelected(pick.id);
    document.getElementById(`problem-${pick.id}`)?.scrollIntoView({ block: "nearest" });
  }

  async function start() {
    if (!selected) return;
    setStarting(true);
    setError(null);
    try {
      store.set("interviewai.lang", language);
      const s = await api.createSession(selected, language);
      navigate(`/interview/${s.session.id}`);
    } catch (e) {
      setError((e as Error).message);
      setStarting(false);
    }
  }

  return (
    <div className="home">
      <section className="hero">
        <h1>Practice a DSA coding round</h1>
        <p className="muted">
          Pick a problem, talk through your approach, write code that runs against hidden tests, and get feedback tied to what you actually said and did.
        </p>
        {!llmReady && (
          <div className="banner info">
            No API key yet, so the interviewer runs an offline script. <button className="link" onClick={onOpenSettings}>Add a Groq key</button> for a real AI interviewer and voice input.
          </div>
        )}
      </section>

      <section className="card">
        <div className="row between wrap">
          <div className="segmented" role="tablist" aria-label="Difficulty">
            {difficulties.map((d) => (
              <button key={d} role="tab" aria-selected={filter === d} className={filter === d ? "on" : ""} onClick={() => setFilter(d)}>
                {d}
              </button>
            ))}
          </div>
          <div className="segmented" role="radiogroup" aria-label="Language">
            {(Object.keys(languageLabel) as Language[]).map((l) => (
              <button key={l} role="radio" aria-checked={language === l} className={language === l ? "on" : ""} onClick={() => setLanguage(l)}>
                {languageLabel[l]}
              </button>
            ))}
          </div>
        </div>

        <div className="row between wrap problem-tools">
          <label className="search">
            <Search size={16} aria-hidden />
            <input type="search" placeholder="Search by name or pattern (e.g. dp, stack)" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search problems" />
          </label>
          <div className="row gap">
            <span className="muted small">{shown.length} of {problems.length} problems</span>
            <button className="ghost" onClick={surprise} disabled={!shown.length}>
              <Shuffle size={16} aria-hidden /> Random
            </button>
          </div>
        </div>

        <ul className="problem-list scroll">
          {shown.map((p) => (
            <li key={p.id} id={`problem-${p.id}`}>
              <button className={selected === p.id ? "problem selected" : "problem"} onClick={() => setSelected(p.id)} onDoubleClick={start}>
                <span className="title">{p.title}</span>
                <span className="muted small">{p.pattern}</span>
                <span className={`pill ${p.difficulty.toLowerCase()}`}>{p.difficulty}</span>
              </button>
            </li>
          ))}
          {!problems.length && !error && <li className="muted">Loading problems...</li>}
          {problems.length > 0 && !shown.length && <li className="muted">No problems match that search.</li>}
        </ul>

        {error && <div className="banner error">{error}</div>}
        <div className="row end">
          <button className="primary large" disabled={!selected || starting} onClick={start}>
            <Play size={16} aria-hidden /> {starting ? "Starting..." : "Start interview"}
          </button>
        </div>
      </section>
    </div>
  );
}

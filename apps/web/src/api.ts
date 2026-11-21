export type Language = "cpp" | "python";
export type Phase = "clarify" | "approach" | "code" | "test" | "complexity" | "wrapup";

export type ProblemSummary = { id: string; title: string; difficulty: "Easy" | "Medium" | "Hard"; pattern: string; test_count: number };
export type Example = { args: unknown[]; expected: unknown; explanation: string };
export type Problem = ProblemSummary & {
  statement: string;
  constraints: string[];
  function: { name: string; params: { name: string; type: string }[]; returns: string };
  examples: Example[];
  hidden_test_count: number;
  hint_count: number;
  starter_code: Record<Language, string>;
};
export type Session = {
  id: string; problem_id: string; language: Language; phase: Phase; phase_label: string; phase_index: number;
  hints_used: number; status: "active" | "ended"; mode: "llm" | "offline"; code: string; created_at: number; ended_at: number | null;
};
export type Message = { id: number; role: "interviewer" | "candidate" | "system" | "hint"; content: string; meta: Record<string, unknown>; created_at: number };
export type TestOutcome = { index: number; hidden: boolean; passed: boolean; status: string; args?: unknown[]; expected?: unknown; actual?: unknown; error?: string | null };
export type RunResult = {
  status: "accepted" | "wrong_answer" | "compile_error" | "runtime_error" | "timeout" | "internal_error";
  passed: number; total: number; elapsed_ms: number; tests: TestOutcome[]; stdout: string; stderr: string; compile_output: string; executor: string;
};
export type Observation = {
  kind: "strength" | "improvement" | "note"; category: string; text: string; source: "measured" | "llm"; verified: boolean;
  evidence: { type: string; quote?: string; message_id?: number; submission_id?: number; [k: string]: unknown };
};
export type Report = {
  session_id: string; generated_at: number; summary: string; observations: Observation[]; llm_used: boolean; llm_error: string | null; disclaimer: string;
  facts: {
    problem: { id: string; title: string; difficulty: string }; language: Language; duration_min: number; hints_used: number; hints_available: number;
    runs: number; submits: number; final_submit: { id: number; status: string; passed: number; total: number } | null; accepted_on_submit: number | null;
    phase_reached: Phase; candidate_messages: number; candidate_words: number; expected_complexity: { time: string; space: string }; mode: string;
  };
};
export type SessionFull = {
  session: Session; problem: Problem; messages: Message[];
  submissions: { id: number; kind: "run" | "submit"; status: string; passed: number; total: number; result: RunResult; created_at: number }[];
  revealed_hints: string[]; report: Report | null;
};
export type HistoryItem = Session & { problem_title: string; difficulty: string | null; best_passed: number | null; submit_total: number | null };
export type Health = { status: string; version: string; executor: string; server_llm_key: boolean; llm_model: string; phases: { id: Phase; label: string }[] };

const BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";
const KEY_STORAGE = "interviewai.llmKey";

export const settings = {
  getKey: () => localStorage.getItem(KEY_STORAGE) ?? "",
  setKey: (k: string) => (k ? localStorage.setItem(KEY_STORAGE, k.trim()) : localStorage.removeItem(KEY_STORAGE))
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const key = settings.getKey();
  if (key) headers.set("X-LLM-Api-Key", key);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let resp: Response;
  try {
    resp = await fetch(`${BASE}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(0, "Cannot reach the InterviewAI API. Is the backend running on port 8000?");
  }
  if (resp.status === 204) return undefined as T;
  const body = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = typeof body.detail === "string" ? body.detail : Array.isArray(body.detail) ? body.detail.map((d: { msg: string }) => d.msg).join("; ") : resp.statusText;
    throw new ApiError(resp.status, detail || `Request failed (${resp.status})`);
  }
  return body as T;
}

const post = <T,>(path: string, data?: unknown) => request<T>(path, { method: "POST", body: data === undefined ? undefined : JSON.stringify(data) });

export const api = {
  health: () => request<Health>("/api/health"),
  problems: () => request<ProblemSummary[]>("/api/problems"),
  createSession: (problem_id: string, language: Language) => post<SessionFull>("/api/sessions", { problem_id, language }),
  session: (id: string) => request<SessionFull>(`/api/sessions/${id}`),
  history: () => request<HistoryItem[]>("/api/sessions"),
  deleteSession: (id: string) => request<void>(`/api/sessions/${id}`, { method: "DELETE" }),
  send: (id: string, text: string, code: string) => post<{ reply: Message; session: Session; hint: string | null }>(`/api/sessions/${id}/messages`, { text, code }),
  hint: (id: string) => post<{ hint: Message; level: number; remaining: number }>(`/api/sessions/${id}/hint`),
  run: (id: string, code: string, language: Language, kind: "run" | "submit") =>
    post<{ submission_id: number; result: RunResult; session: Session }>(`/api/sessions/${id}/run`, { code, language, kind }),
  end: (id: string, code: string) => post<Report>(`/api/sessions/${id}/end`, { code }),
  transcribe: (blob: Blob) => {
    const form = new FormData();
    form.append("file", blob, "answer.webm");
    return request<{ text: string }>("/api/speech/transcribe", { method: "POST", body: form });
  }
};

export const languageLabel: Record<Language, string> = { cpp: "C++", python: "Python" };

export function formatValue(v: unknown): string {
  return JSON.stringify(v);
}

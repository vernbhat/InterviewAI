import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { api, HistoryItem, languageLabel } from "../api";
import { navigate } from "../App";
import { confirmDialog } from "../components/Confirm";

export function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => api.history().then(setItems, (e: Error) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  async function remove(id: string) {
    if (!(await confirmDialog("Delete this interview and its report?", "Delete"))) return;
    await api.deleteSession(id).catch((e: Error) => setError(e.message));
    load();
  }

  return (
    <div className="history">
      <h1>Interview history</h1>
      {error && <div className="banner error">{error}</div>}
      {items && items.length === 0 && (
        <p className="muted">
          No interviews yet. <a href="#/">Start one</a>.
        </p>
      )}
      {items && items.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Problem</th>
              <th>Lang</th>
              <th>Best submit</th>
              <th>Hints</th>
              <th>Status</th>
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.id} onClick={() => navigate(s.status === "ended" ? `/report/${s.id}` : `/interview/${s.id}`)} className="clickable">
                <td>{new Date(s.created_at * 1000).toLocaleString()}</td>
                <td>
                  {s.problem_title} {s.difficulty && <span className={`pill ${s.difficulty.toLowerCase()}`}>{s.difficulty}</span>}
                </td>
                <td>{languageLabel[s.language]}</td>
                <td className="mono">{s.best_passed !== null && s.submit_total ? `${s.best_passed}/${s.submit_total}` : "–"}</td>
                <td>{s.hints_used}</td>
                <td>{s.status === "ended" ? "Report ready" : "In progress"}</td>
                <td>
                  <button
                    className="icon"
                    aria-label="Delete interview"
                    onClick={(e) => {
                      e.stopPropagation();
                      remove(s.id);
                    }}
                  >
                    <Trash2 size={15} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

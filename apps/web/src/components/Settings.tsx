import { useState } from "react";
import { X } from "lucide-react";
import { Health, settings } from "../api";

export function SettingsDialog({ health, onClose }: { health: Health | null; onClose: () => void }) {
  const [key, setKey] = useState(settings.getKey());
  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-labelledby="settings-title" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-head">
          <h2 id="settings-title">Settings</h2>
          <button className="icon" onClick={onClose} aria-label="Close settings">
            <X size={18} />
          </button>
        </div>
        <label htmlFor="llm-key">LLM API key (Groq or any OpenAI-compatible provider)</label>
        <input id="llm-key" type="password" autoComplete="off" placeholder="gsk_..." value={key} onChange={(e) => setKey(e.target.value)} />
        <p className="muted small">
          Stored only in this browser and sent with each request in the <code>X-LLM-Api-Key</code> header. Without a key the interviewer runs a fixed offline
          script and voice input is disabled. A free Groq key covers roughly five full interviews a day.
        </p>
        {health && (
          <dl className="kv small">
            <dt>Server key</dt>
            <dd>{health.server_llm_key ? "configured" : "not configured"}</dd>
            <dt>Model</dt>
            <dd>{health.llm_model}</dd>
            <dt>Code runner</dt>
            <dd>{health.executor === "judge0" ? "Judge0" : "local (development only, not sandboxed)"}</dd>
            <dt>Version</dt>
            <dd>{health.version}</dd>
          </dl>
        )}
        <div className="row end">
          <button
            className="ghost"
            onClick={() => {
              settings.setKey("");
              setKey("");
            }}
          >
            Clear key
          </button>
          <button
            className="primary"
            onClick={() => {
              settings.setKey(key);
              onClose();
            }}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

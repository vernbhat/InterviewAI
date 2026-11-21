import { useState } from "react";
import { X } from "lucide-react";
import { api, Health, settings } from "../api";

export function SettingsDialog({ health, onClose }: { health: Health | null; onClose: () => void }) {
  const [key, setKey] = useState(settings.getKey());
  const canSave = Boolean(health?.can_save_key);
  const [remember, setRemember] = useState(true);
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function save() {
    const k = key.trim();
    if (canSave && remember && k) {
      setSaving(true);
      try {
        const r = await api.saveServerKey(k);
        settings.setKey(""); // the server has it now, no need to keep a copy in the browser
        setStatus(`Saved to ${r.path}`);
        setSaving(false);
        setTimeout(onClose, 900);
        return;
      } catch (e) {
        setSaving(false);
        setStatus(`Couldn't save to .env: ${(e as Error).message}`);
        return;
      }
    }
    settings.setKey(k);
    onClose();
  }
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
        {canSave && (
          <label className="check small">
            <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
            <span>
              Remember it in the <code>.env</code> file on this computer, so you never have to paste it again
            </span>
          </label>
        )}
        {status && <p className="small">{status}</p>}
        <p className="muted small">
          {canSave && remember && (
            <>
              The key is written to <code>.env</code> in the project folder. That file is git-ignored, so it never gets committed.{" "}
            </>
          )}
          {canSave && remember ? "Without this option it's s" : "S"}tored only in this browser and sent with each request in the <code>X-LLM-Api-Key</code> header. Without a key the interviewer runs a fixed offline
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
          <button className="primary" onClick={save} disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}

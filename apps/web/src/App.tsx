import { useEffect, useState } from "react";
import { History as HistoryIcon, KeyRound, TerminalSquare } from "lucide-react";
import { api, Health, settings } from "./api";
import { Home } from "./pages/Home";
import { Interview } from "./pages/Interview";
import { ReportPage } from "./pages/Report";
import { HistoryPage } from "./pages/History";
import { SettingsDialog } from "./components/Settings";

type Route = { name: "home" } | { name: "interview"; id: string } | { name: "report"; id: string } | { name: "history" };

function parseRoute(hash: string): Route {
  const parts = hash.replace(/^#\/?/, "").split("/");
  if (parts[0] === "interview" && parts[1]) return { name: "interview", id: parts[1] };
  if (parts[0] === "report" && parts[1]) return { name: "report", id: parts[1] };
  if (parts[0] === "history") return { name: "history" };
  return { name: "home" };
}

export const navigate = (path: string) => {
  window.location.hash = path;
};

export function App() {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.hash));
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [hasKey, setHasKey] = useState(Boolean(settings.getKey()));

  useEffect(() => {
    const onHash = () => setRoute(parseRoute(window.location.hash));
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    api.health().then(setHealth, (e: Error) => setHealthError(e.message));
  }, []);

  const llmReady = hasKey || Boolean(health?.server_llm_key);

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="#/">
          <TerminalSquare size={20} aria-hidden /> InterviewAI
        </a>
        <nav>
          <a href="#/history" className={route.name === "history" ? "active" : ""}>
            <HistoryIcon size={16} aria-hidden /> History
          </a>
          <button className="ghost" onClick={() => setShowSettings(true)}>
            <KeyRound size={16} aria-hidden /> {llmReady ? "AI interviewer on" : "Offline mode"}
          </button>
        </nav>
      </header>
      {healthError && <div className="banner error">{healthError}</div>}
      <main className={route.name === "interview" ? "main full" : "main"}>
        {route.name === "home" && <Home llmReady={llmReady} onOpenSettings={() => setShowSettings(true)} />}
        {route.name === "interview" && <Interview key={route.id} id={route.id} />}
        {route.name === "report" && <ReportPage key={route.id} id={route.id} />}
        {route.name === "history" && <HistoryPage />}
      </main>
      {showSettings && (
        <SettingsDialog
          health={health}
          onClose={() => {
            setShowSettings(false);
            setHasKey(Boolean(settings.getKey()));
          }}
        />
      )}
    </div>
  );
}

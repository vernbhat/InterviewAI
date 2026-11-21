import { useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";

// In-page replacement for window.confirm, which hosted preview iframes suppress.
function ConfirmDialog({ message, confirmLabel, onDone }: { message: string; confirmLabel: string; onDone: (ok: boolean) => void }) {
  const okRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    okRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onDone(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onDone]);
  return (
    <div className="overlay" role="alertdialog" aria-modal="true" aria-labelledby="confirm-msg" onClick={() => onDone(false)}>
      <div className="dialog confirm" onClick={(e) => e.stopPropagation()}>
        <p id="confirm-msg">{message}</p>
        <div className="row end">
          <button className="ghost" onClick={() => onDone(false)}>Cancel</button>
          <button className="primary" ref={okRef} onClick={() => onDone(true)}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  );
}

export function confirmDialog(message: string, confirmLabel = "Confirm"): Promise<boolean> {
  return new Promise((resolve) => {
    const host = document.createElement("div");
    document.body.appendChild(host);
    const root = createRoot(host);
    const done = (ok: boolean) => {
      root.unmount();
      host.remove();
      resolve(ok);
    };
    root.render(<ConfirmDialog message={message} confirmLabel={confirmLabel} onDone={done} />);
  });
}

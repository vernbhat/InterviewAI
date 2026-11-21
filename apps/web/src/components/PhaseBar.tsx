import type { Phase } from "../api";

const phases: { id: Phase; label: string }[] = [
  { id: "clarify", label: "Clarify" },
  { id: "approach", label: "Approach" },
  { id: "code", label: "Code" },
  { id: "test", label: "Test" },
  { id: "complexity", label: "Complexity" },
  { id: "wrapup", label: "Wrap up" }
];

export function PhaseBar({ current }: { current: Phase }) {
  const idx = phases.findIndex((p) => p.id === current);
  return (
    <ol className="phasebar" aria-label="Interview phase">
      {phases.map((p, i) => (
        <li key={p.id} className={i < idx ? "done" : i === idx ? "current" : ""} aria-current={i === idx ? "step" : undefined}>
          {p.label}
        </li>
      ))}
    </ol>
  );
}

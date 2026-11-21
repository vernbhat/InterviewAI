import { KeyboardEvent, PointerEvent, useRef } from "react";

type Props = {
  orientation: "vertical" | "horizontal"; // vertical = a bar between side-by-side panes
  label: string;
  onDrag: (delta: number) => void; // pixels moved since the last call
  onReset?: () => void;
};

/** Drag handle between two panes. Works with mouse, touch, and arrow keys; double-click resets. */
export function Splitter({ orientation, label, onDrag, onReset }: Props) {
  const last = useRef<number | null>(null);
  const pos = (e: PointerEvent) => (orientation === "vertical" ? e.clientX : e.clientY);

  return (
    <div
      className={`splitter ${orientation}`}
      role="separator"
      aria-orientation={orientation}
      aria-label={label}
      tabIndex={0}
      title="Drag to resize, double-click to reset"
      onPointerDown={(e) => {
        e.preventDefault();
        (e.target as HTMLElement).setPointerCapture(e.pointerId);
        last.current = pos(e);
        document.body.classList.add(orientation === "vertical" ? "resizing-x" : "resizing-y");
      }}
      onPointerMove={(e) => {
        if (last.current === null) return;
        const p = pos(e);
        onDrag(p - last.current);
        last.current = p;
      }}
      onPointerUp={(e) => {
        last.current = null;
        (e.target as HTMLElement).releasePointerCapture(e.pointerId);
        document.body.classList.remove("resizing-x", "resizing-y");
      }}
      onDoubleClick={onReset}
      onKeyDown={(e: KeyboardEvent) => {
        const step = e.shiftKey ? 80 : 24;
        const back = orientation === "vertical" ? "ArrowLeft" : "ArrowUp";
        const fwd = orientation === "vertical" ? "ArrowRight" : "ArrowDown";
        if (e.key === back) onDrag(-step);
        else if (e.key === fwd) onDrag(step);
        else return;
        e.preventDefault();
      }}
    />
  );
}

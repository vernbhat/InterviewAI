import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor/editor/editor.api";
import "monaco-editor/languages/definitions/cpp/register";
import "monaco-editor/languages/definitions/python/register";
import EditorWorker from "monaco-editor/editor/editor.worker?worker";
import type { Language } from "../api";

// Bundle Monaco locally instead of loading it from a CDN, so self-hosted installs work offline.
(self as unknown as { MonacoEnvironment: unknown }).MonacoEnvironment = { getWorker: () => new EditorWorker() };
loader.config({ monaco });

type Props = { language: Language; value: string; onChange: (v: string) => void; readOnly?: boolean; onRun?: () => void };

export function CodeEditor({ language, value, onChange, readOnly, onRun }: Props) {
  return (
    <Editor
      height="100%"
      theme="vs"
      language={language === "cpp" ? "cpp" : "python"}
      value={value}
      onChange={(v) => onChange(v ?? "")}
      onMount={(editor) => {
        if (onRun) editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, onRun);
      }}
      options={{
        readOnly,
        minimap: { enabled: false },
        fontSize: 14,
        tabSize: 4,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        renderLineHighlight: "line",
        padding: { top: 12 }
      }}
    />
  );
}

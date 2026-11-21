import { useRef, useState } from "react";
import { Mic, Square } from "lucide-react";
import { api } from "../api";

/** Click to start recording, click again to stop and transcribe (Groq Whisper). */
export function PushToTalk({ enabled, onText, onError }: { enabled: boolean; onText: (t: string) => void; onError: (m: string) => void }) {
  const [state, setState] = useState<"idle" | "recording" | "transcribing">("idle");
  const recorder = useRef<MediaRecorder | null>(null);

  async function start() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];
      rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setState("transcribing");
        try {
          const { text } = await api.transcribe(new Blob(chunks, { type: rec.mimeType || "audio/webm" }));
          if (text) onText(text);
        } catch (e) {
          onError((e as Error).message);
        } finally {
          setState("idle");
        }
      };
      rec.start();
      recorder.current = rec;
      setState("recording");
    } catch {
      onError("Microphone access was blocked or is unavailable.");
    }
  }

  const title = !enabled ? "Voice input needs an API key (Settings)" : state === "recording" ? "Stop and transcribe" : "Speak your answer";
  return (
    <button
      className={state === "recording" ? "icon recording" : "icon"}
      disabled={!enabled || state === "transcribing"}
      title={title}
      aria-label={title}
      onClick={() => (state === "recording" ? recorder.current?.stop() : start())}
    >
      {state === "recording" ? <Square size={16} /> : <Mic size={16} />}
    </button>
  );
}

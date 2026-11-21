import React from "react";

/** Tiny, safe renderer for **bold**, _italic_ and `code` spans. No HTML is injected. */
export function Inline({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|_[^_]+_)/g).filter(Boolean);
  return (
    <>
      {parts.map((p, i) => {
        if (p.startsWith("**") && p.endsWith("**")) return <strong key={i}>{p.slice(2, -2)}</strong>;
        if (p.startsWith("`") && p.endsWith("`")) return <code key={i}>{p.slice(1, -1)}</code>;
        if (p.startsWith("_") && p.endsWith("_") && p.length > 2) return <em key={i}>{p.slice(1, -1)}</em>;
        return <React.Fragment key={i}>{p}</React.Fragment>;
      })}
    </>
  );
}

export function Paragraphs({ text }: { text: string }) {
  return (
    <>
      {text.split(/\n{2,}/).map((para, i) => (
        <p key={i}>
          {para.split("\n").map((line, j) => (
            <React.Fragment key={j}>
              {j > 0 && <br />}
              <Inline text={line} />
            </React.Fragment>
          ))}
        </p>
      ))}
    </>
  );
}

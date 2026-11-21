// localStorage throws in sandboxed / opaque-origin iframes (e.g. hosted previews).
// Fall back to an in-memory map so the app keeps working, just without persistence.
const memory = new Map<string, string>();

function ls(): Storage | null {
  try {
    const s = window.localStorage;
    const probe = "__interviewai_probe__";
    s.setItem(probe, "1");
    s.removeItem(probe);
    return s;
  } catch {
    return null;
  }
}
const backing = ls();

export const store = {
  get(key: string): string | null {
    return backing ? backing.getItem(key) : memory.get(key) ?? null;
  },
  set(key: string, value: string): void {
    if (backing) backing.setItem(key, value);
    else memory.set(key, value);
  },
  remove(key: string): void {
    if (backing) backing.removeItem(key);
    else memory.delete(key);
  }
};

// A tiny cache of the signed-in user so supervisor routes still open offline (the cookie stays valid).
import type { MeOut } from "../api/types";

const KEY = "nool.me";
const LANG = "nool.lang";

export function getCachedMe(): MeOut | null {
  try { return JSON.parse(localStorage.getItem(KEY) ?? "null") as MeOut | null; } catch { return null; }
}
export function setCachedMe(me: MeOut | null): void {
  try { if (me) localStorage.setItem(KEY, JSON.stringify(me)); else localStorage.removeItem(KEY); } catch { /* private mode */ }
}
export function getStoredLang(): "en" | "ta" | null {
  try { const v = localStorage.getItem(LANG); return v === "ta" || v === "en" ? v : null; } catch { return null; }
}
export function setStoredLang(l: "en" | "ta"): void {
  try { localStorage.setItem(LANG, l); } catch { /* ignore */ }
}

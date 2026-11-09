import type { Lang } from "../i18n/t";

// Latin digits in both languages for clarity on the floor (Doc2 section 8); only month names localise.
const locale = (lang: Lang) => (lang === "ta" ? "ta-IN-u-nu-latn" : "en-GB");

export function parseIso(iso: string): Date {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}
export function fmtDate(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat(locale(lang), { day: "numeric", month: "short", timeZone: "UTC" }).format(parseIso(iso));
}
export function fmtDateYear(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat(locale(lang), { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(parseIso(iso));
}
export function fmtDateTime(iso: string, lang: Lang): string {
  return new Intl.DateTimeFormat(locale(lang), { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(iso));
}
export const fmtNum = (n: number): string => Math.round(n).toLocaleString("en-US");
export const pct = (done: number, qty: number): number => (qty > 0 ? Math.min(100, Math.round((100 * done) / qty)) : 0);
export const todayIso = (): string => new Date().toISOString().slice(0, 10);

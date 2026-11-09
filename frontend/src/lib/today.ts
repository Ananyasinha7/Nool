import { useSyncExternalStore } from "react";
import { todayIso } from "./format";

// "Today" comes from the server (GET /healthz) so entries are dated with the demo clock and survive a
// phone whose date is wrong. It is cached so it is still known offline; the device date is the last resort.
const KEY = "nool.today";
let current: string | null = (() => { try { return localStorage.getItem(KEY); } catch { return null; } })();
const listeners = new Set<() => void>();

export function setToday(iso: string): void {
  if (iso === current) return;
  current = iso;
  try { localStorage.setItem(KEY, iso); } catch { /* ignore */ }
  listeners.forEach((l) => l());
}
export function getToday(): string { return current ?? todayIso(); }
export function useToday(): string {
  return useSyncExternalStore((cb) => { listeners.add(cb); return () => { listeners.delete(cb); }; }, getToday);
}
export function isDemoClock(iso: string): boolean { return iso !== todayIso(); }

// Offline sync engine (Doc3 section 10). Re-sending is always safe: the server uses the client UUID as the key.
import { db } from "./db";
import { SENT_RETENTION_MS } from "./queue";
import type { OutboxItem } from "./types";

export const MAX_ATTEMPTS = 8;
export const BACKOFF_BASE_MS = 2000;
export const BACKOFF_CAP_MS = 300_000;

/** 2 s, 4 s, 8 s ... capped at 5 min. */
export const backoffMs = (attempts: number): number => Math.min(BACKOFF_BASE_MS * 2 ** (attempts - 1), BACKOFF_CAP_MS);

export interface Transport {
  postLog: (log: NonNullable<OutboxItem["log"]>) => Promise<Response>;
  postPhoto: (logId: string, photoId: string, blob: Blob) => Promise<Response>;
  postAudio: (logId: string, blob: Blob) => Promise<Response>;
}
export interface SyncDeps { transport: Transport; now?: () => number }
export interface DrainResult { sent: number; failed: number; retrying: number; paused: boolean }

type Listener = () => void;
const listeners = new Set<Listener>();
let paused = false;
let draining = false;

export const isPaused = (): boolean => paused;
export const onSyncChange = (l: Listener): (() => void) => { listeners.add(l); return () => { listeners.delete(l); }; };
const notify = () => listeners.forEach((l) => l());

/** After a successful sign-in the 401 pause ends and the queue continues: nothing was lost. */
export function resume(): void { paused = false; notify(); }
export function _resetForTests(): void { paused = false; draining = false; listeners.clear(); }

async function messageOf(res: Response): Promise<string> {
  try { const b = (await res.json()) as { error?: { message?: string } }; return b.error?.message ?? res.statusText; }
  catch { return res.statusText || `HTTP ${res.status}`; }
}

async function send(item: OutboxItem, t: Transport): Promise<Response> {
  if (item.type === "log" && item.log) return t.postLog(item.log);
  if (item.type === "photo" && item.blob && item.parentLogId) return t.postPhoto(item.parentLogId, item.id, item.blob);
  if (item.type === "audio" && item.blob && item.parentLogId) return t.postAudio(item.parentLogId, item.blob);
  throw new Error("malformed outbox item");
}

/** Media may only go once its log is on the server: numbers are never blocked by media. */
async function parentAllows(item: OutboxItem): Promise<boolean> {
  if (!item.parentLogId) return true;
  const parent = await db.outbox.get(item.parentLogId);
  return !parent || parent.state === "SENT"; // parent gone = already sent and cleaned up
}

export async function drain(deps: SyncDeps): Promise<DrainResult> {
  const now = deps.now ?? Date.now;
  const result: DrainResult = { sent: 0, failed: 0, retrying: 0, paused };
  if (draining || paused) return result; // one drain at a time: no double sends
  draining = true;
  try {
    // A SENDING item at start means the app died mid-request. Re-sending is safe (idempotent).
    await db.outbox.where("state").equals("SENDING").modify({ state: "QUEUED" });
    const due = (await db.outbox.where("state").equals("QUEUED").sortBy("createdAt")).filter((i) => i.nextAttemptAt <= now());
    for (const item of due) {
      if (paused) break;
      if (!(await parentAllows(item))) continue;
      await db.outbox.update(item.id, { state: "SENDING" });
      notify();
      let res: Response | null = null;
      try { res = await send(item, deps.transport); } catch { res = null; } // network error
      if (res && res.status >= 200 && res.status < 300) {
        await db.outbox.update(item.id, { state: "SENT", sentAt: now(), lastError: null });
        result.sent++;
      } else if (res && res.status === 401) {
        await db.outbox.update(item.id, { state: "QUEUED" }); // keep it; just stop until signed in again
        paused = true; result.paused = true;
        notify();
        break;
      } else if (res && [400, 403, 409, 413, 422].includes(res.status)) {
        await db.outbox.update(item.id, { state: "FAILED", lastError: await messageOf(res) }); // no auto retry
        result.failed++;
      } else {
        const attempts = item.attempts + 1; // 5xx, 408, 429 or network error
        if (attempts >= MAX_ATTEMPTS) {
          await db.outbox.update(item.id, { state: "FAILED", attempts, lastError: res ? `HTTP ${res.status}` : "No connection" });
          result.failed++;
        } else {
          await db.outbox.update(item.id, { state: "QUEUED", attempts, lastError: res ? `HTTP ${res.status}` : "No connection", nextAttemptAt: now() + backoffMs(attempts) });
          result.retrying++;
        }
      }
      notify();
    }
    // Housekeeping: delete SENT items after 24 h (kept briefly so "Sent" can be shown).
    const cutoff = now() - SENT_RETENTION_MS;
    await db.outbox.where("state").equals("SENT").filter((i) => (i.sentAt ?? 0) < cutoff).delete();
  } finally { draining = false; notify(); }
  return result;
}

/** Earliest time a queued item becomes due again (for scheduling the next attempt), or null. */
export async function nextDueAt(): Promise<number | null> {
  const queued = await db.outbox.where("state").equals("QUEUED").toArray();
  return queued.length ? Math.min(...queued.map((i) => i.nextAttemptAt)) : null;
}

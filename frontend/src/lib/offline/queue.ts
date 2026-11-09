import { liveQuery } from "dexie";
import type { LogInput } from "../../api/types";
import { db } from "./db";
import type { OutboxItem, QueueCounts } from "./types";
import { generateUUID } from "../uuid";

export const SENT_RETENTION_MS = 24 * 3600 * 1000;
const newId = () => generateUUID();

/** Saves a log (and optional photo/audio) in ONE transaction: after this resolves the entry is durable
 * on the phone, whatever the network does. That is what lets Send return in under 600 ms. */
export async function enqueueLog(log: LogInput, label: string, opts: { photo?: Blob; audio?: Blob } = {}, now = Date.now()): Promise<void> {
  const base = { state: "QUEUED" as const, attempts: 0, lastError: null, nextAttemptAt: 0, createdAt: now, label };
  await db.transaction("rw", db.outbox, async () => {
    await db.outbox.put({ ...base, id: log.id, type: "log", log });
    if (opts.photo) await db.outbox.put({ ...base, id: newId(), type: "photo", blob: opts.photo, parentLogId: log.id, createdAt: now + 1 });
    if (opts.audio) await db.outbox.put({ ...base, id: newId(), type: "audio", blob: opts.audio, parentLogId: log.id, createdAt: now + 2 });
  });
}

export const listItems = (): Promise<OutboxItem[]> => db.outbox.orderBy("createdAt").toArray();

export function countsOf(items: OutboxItem[], paused: boolean): QueueCounts {
  return {
    queued: items.filter((i) => i.state === "QUEUED").length,
    sending: items.filter((i) => i.state === "SENDING").length,
    failed: items.filter((i) => i.state === "FAILED").length,
    paused,
  };
}

/** A failed item never disappears: Retry puts it back with a clean slate. */
export async function retryItem(id: string): Promise<void> {
  await db.outbox.update(id, { state: "QUEUED", attempts: 0, lastError: null, nextAttemptAt: 0 });
}
export async function retryAllFailed(): Promise<void> {
  const failed = await db.outbox.where("state").equals("FAILED").toArray();
  await Promise.all(failed.map((f) => retryItem(f.id)));
}

/** Edit a failed log (e.g. the server rejected the number) and queue it again. Same id: still idempotent. */
export async function editFailedLog(id: string, patch: { qty?: number; noteText?: string | null }): Promise<void> {
  await db.transaction("rw", db.outbox, async () => {
    const it = await db.outbox.get(id);
    if (!it?.log) return;
    await db.outbox.put({ ...it, log: { ...it.log, ...patch }, state: "QUEUED", attempts: 0, lastError: null, nextAttemptAt: 0 });
  });
}

export const removeItem = (id: string): Promise<void> => db.outbox.delete(id);

/** Live view for the UI (queue chip and sheet). */
export function watchItems(cb: (items: OutboxItem[]) => void): () => void {
  const sub = liveQuery(() => db.outbox.orderBy("createdAt").toArray()).subscribe({ next: cb, error: () => undefined });
  return () => sub.unsubscribe();
}

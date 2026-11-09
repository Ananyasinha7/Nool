import "fake-indexeddb/auto";
import { beforeEach, describe, expect, it } from "vitest";
import type { LogInput } from "../../api/types";
import { db } from "./db";
import { enqueueLog, listItems, retryItem } from "./queue";
import { BACKOFF_CAP_MS, MAX_ATTEMPTS, _resetForTests, backoffMs, drain, isPaused, resume, type Transport } from "./sync";

const log = (id: string, qty = 100): LogInput => ({
  id, orderId: "o1", stageKey: "STITCHING", logDate: "2026-11-03", qty, noteText: null, clientCreatedAt: "2026-11-03T06:00:00Z",
});
const json = (status: number, body: unknown = {}) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

/** A fake server that behaves like the real one: the client UUID is the key. */
function fakeServer() {
  const logs = new Map<string, LogInput>();
  const photos = new Set<string>();
  const calls: string[] = [];
  let mode: "ok" | "offline" | "500" | "401" | "422" = "ok";
  const gate = (): Response | "throw" | null => {
    if (mode === "offline") return "throw";
    if (mode === "500") return json(500);
    if (mode === "401") return json(401, { error: { code: "UNAUTHENTICATED", message: "Please sign in." } });
    if (mode === "422") return json(422, { error: { code: "VALIDATION", message: "That would be more than the order quantity allows." } });
    return null;
  };
  const transport: Transport = {
    postLog: async (l) => { calls.push(`log:${l.id}`); const g = gate(); if (g === "throw") throw new TypeError("offline"); if (g) return g;
      const dup = logs.has(l.id); logs.set(l.id, l); return json(dup ? 200 : 201, { id: l.id, effective: true }); },
    postPhoto: async (_log, pid) => { calls.push(`photo:${pid}`); const g = gate(); if (g === "throw") throw new TypeError("offline"); if (g) return g; photos.add(pid); return json(201, { id: pid }); },
    postAudio: async () => json(201, { ok: true }),
  };
  return { transport, logs, photos, calls, setMode: (m: typeof mode) => { mode = m; } };
}

let clock = 1_000_000;
const now = () => clock;
beforeEach(async () => { await db.outbox.clear(); _resetForTests(); clock = 1_000_000; });

describe("offline sync (gate G1)", () => {
  it("airplane mode -> submit -> reconnect -> exactly one effective row", async () => {
    const s = fakeServer();
    s.setMode("offline");
    await enqueueLog(log("a"), "x", {}, clock);
    const first = await drain({ transport: s.transport, now });
    expect(first.retrying).toBe(1);
    expect((await listItems())[0]).toMatchObject({ state: "QUEUED", attempts: 1 });
    expect(s.logs.size).toBe(0);
    s.setMode("ok");
    clock += 2001; // backoff elapsed
    const second = await drain({ transport: s.transport, now });
    expect(second.sent).toBe(1);
    expect(s.logs.size).toBe(1);
    expect((await listItems())[0].state).toBe("SENT");
  });

  it("a repeated send is harmless (server idempotent) and two drains never double-send", async () => {
    const s = fakeServer();
    await enqueueLog(log("a"), "x", {}, clock);
    await Promise.all([drain({ transport: s.transport, now }), drain({ transport: s.transport, now })]);
    expect(s.calls.filter((c) => c === "log:a")).toHaveLength(1);
    await db.outbox.update("a", { state: "QUEUED" }); // a lost response: the client re-sends
    await drain({ transport: s.transport, now });
    expect(s.logs.size).toBe(1);
  });

  it("401 pauses without dropping the queue; resume continues", async () => {
    const s = fakeServer();
    s.setMode("401");
    await enqueueLog(log("a"), "x", {}, clock);
    await enqueueLog(log("b"), "y", {}, clock + 5);
    const r = await drain({ transport: s.transport, now });
    expect(r.paused).toBe(true);
    expect(isPaused()).toBe(true);
    const items = await listItems();
    expect(items.map((i) => i.state)).toEqual(["QUEUED", "QUEUED"]); // nothing lost
    expect((await drain({ transport: s.transport, now })).sent).toBe(0); // still paused
    s.setMode("ok"); resume();
    expect((await drain({ transport: s.transport, now })).sent).toBe(2);
  });

  it("a server rejection (422) fails the item with the reason and does not retry; Retry works", async () => {
    const s = fakeServer();
    s.setMode("422");
    await enqueueLog(log("a", 99999), "x", {}, clock);
    const r = await drain({ transport: s.transport, now });
    expect(r.failed).toBe(1);
    const it = (await listItems())[0];
    expect(it.state).toBe("FAILED");
    expect(it.lastError).toContain("more than the order quantity");
    clock += 10 * 60_000;
    expect((await drain({ transport: s.transport, now })).sent).toBe(0); // no automatic retry
    s.setMode("ok");
    await retryItem("a");
    expect((await drain({ transport: s.transport, now })).sent).toBe(1);
  });

  it("photos wait for their log", async () => {
    const s = fakeServer();
    s.setMode("500");
    await enqueueLog(log("a"), "x", { photo: new Blob(["img"]) }, clock);
    await drain({ transport: s.transport, now });
    expect(s.calls.every((c) => c.startsWith("log:"))).toBe(true); // photo never attempted
    s.setMode("ok");
    clock += 2001;
    await drain({ transport: s.transport, now });
    expect(s.logs.size).toBe(1);
    expect(s.photos.size).toBe(1);
    expect((await listItems()).every((i) => i.state === "SENT")).toBe(true);
  });

  it("backoff is 2s, 4s, 8s ... capped at 5 minutes", () => {
    expect([1, 2, 3, 4].map(backoffMs)).toEqual([2000, 4000, 8000, 16000]);
    expect(backoffMs(20)).toBe(BACKOFF_CAP_MS);
  });

  it("not due yet: nothing is sent before the backoff elapses", async () => {
    const s = fakeServer();
    s.setMode("offline");
    await enqueueLog(log("a"), "x", {}, clock);
    await drain({ transport: s.transport, now });
    s.setMode("ok");
    expect((await drain({ transport: s.transport, now })).sent).toBe(0); // same instant
  });

  it("gives up after 8 attempts but keeps the item for manual retry", async () => {
    const s = fakeServer();
    s.setMode("500");
    await enqueueLog(log("a"), "x", {}, clock);
    for (let i = 0; i < MAX_ATTEMPTS; i++) { await drain({ transport: s.transport, now }); clock += BACKOFF_CAP_MS + 1; }
    const it = (await listItems())[0];
    expect(it.state).toBe("FAILED");
    expect(it.attempts).toBe(MAX_ATTEMPTS);
  });

  it("an item stuck in SENDING after a crash is retried safely", async () => {
    const s = fakeServer();
    await enqueueLog(log("a"), "x", {}, clock);
    await db.outbox.update("a", { state: "SENDING" });
    expect((await drain({ transport: s.transport, now })).sent).toBe(1);
  });

  it("SENT items are cleaned up after 24 hours", async () => {
    const s = fakeServer();
    await enqueueLog(log("a"), "x", {}, clock);
    await drain({ transport: s.transport, now });
    expect(await listItems()).toHaveLength(1);
    clock += 25 * 3600 * 1000;
    await drain({ transport: s.transport, now });
    expect(await listItems()).toHaveLength(0);
  });
});

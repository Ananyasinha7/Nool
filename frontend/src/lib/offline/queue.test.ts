import "fake-indexeddb/auto";
import { beforeEach, describe, expect, it } from "vitest";
import type { LogInput } from "../../api/types";
import { db } from "./db";
import { countsOf, editFailedLog, enqueueLog, listItems, retryItem } from "./queue";

const log = (id: string = crypto.randomUUID(), qty = 100): LogInput => ({
  id, orderId: "o1", stageKey: "STITCHING", logDate: "2026-11-03", qty, noteText: null, clientCreatedAt: "2026-11-03T06:00:00Z",
});

beforeEach(async () => { await db.outbox.clear(); });

describe("outbox queue", () => {
  it("saves log, photo and audio together", async () => {
    await enqueueLog(log("a"), "B-PO · STITCHING", { photo: new Blob(["p"]), audio: new Blob(["a"]) });
    const items = await listItems();
    expect(items.map((i) => i.type)).toEqual(["log", "photo", "audio"]);
    expect(items[1].parentLogId).toBe("a");
    expect(items.every((i) => i.state === "QUEUED")).toBe(true);
  });
  it("counts states", async () => {
    await enqueueLog(log("a"), "x");
    await db.outbox.update("a", { state: "FAILED" });
    await enqueueLog(log("b"), "y");
    expect(countsOf(await listItems(), true)).toEqual({ queued: 1, sending: 0, failed: 1, paused: true });
  });
  it("retry puts a failed item back with a clean slate", async () => {
    await enqueueLog(log("a"), "x");
    await db.outbox.update("a", { state: "FAILED", attempts: 8, lastError: "boom", nextAttemptAt: 99 });
    await retryItem("a");
    expect(await db.outbox.get("a")).toMatchObject({ state: "QUEUED", attempts: 0, lastError: null, nextAttemptAt: 0 });
  });
  it("editing a failed log keeps its id (still idempotent) and requeues it", async () => {
    await enqueueLog(log("a", 999), "x");
    await db.outbox.update("a", { state: "FAILED", lastError: "too many" });
    await editFailedLog("a", { qty: 50 });
    const it = await db.outbox.get("a");
    expect(it?.log?.qty).toBe(50);
    expect(it?.state).toBe("QUEUED");
  });
});

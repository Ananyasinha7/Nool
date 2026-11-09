import Dexie, { type Table } from "dexie";
import type { CachedCards, OutboxItem } from "./types";

class NoolDB extends Dexie {
  outbox!: Table<OutboxItem, string>;
  cache!: Table<CachedCards & { key: string }, string>;
  constructor() {
    super("nool");
    this.version(1).stores({ outbox: "id, state, createdAt, parentLogId", cache: "key" });
  }
}
export const db = new NoolDB();

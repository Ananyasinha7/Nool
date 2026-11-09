// Client-only types: not part of the API contract (Doc3 section 5.3).
import type { LogInput, SupOrderCard } from "../../api/types";

export type ItemType = "log" | "photo" | "audio";
export type ItemState = "QUEUED" | "SENDING" | "SENT" | "FAILED";

export interface OutboxItem {
  id: string;                 // client UUID = idempotency key (log id, photo id, or audio id)
  type: ItemType;
  log?: LogInput;             // type === "log"
  blob?: Blob;                // photo or audio
  parentLogId?: string;       // media waits for its log: numbers are never blocked by media
  state: ItemState;
  attempts: number;
  lastError: string | null;
  nextAttemptAt: number;      // epoch ms: backoff
  createdAt: number;
  sentAt?: number;
  label: string;              // human label for the queue sheet, e.g. "B-PO-88213 · STITCHING"
}

export interface QueueCounts { queued: number; sending: number; failed: number; paused: boolean }
export interface CachedCards { cards: SupOrderCard[]; fetchedAt: number }

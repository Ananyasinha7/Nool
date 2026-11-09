import type { SupOrderCard } from "../../api/types";
import { getToday } from "../today";
import { generateUUID } from "../uuid";
import { enqueueLog } from "./queue";
import { triggerSync } from "./runtime";

export interface SubmitArgs { card: SupOrderCard; qty: number; note?: string; photo?: Blob; audio?: Blob }

/** Saves to the local queue and returns: the supervisor never waits on the network (Doc2 S-7). */
export async function submitEntry({ card, qty, note, photo, audio }: SubmitArgs): Promise<string> {
  const id = generateUUID();
  await enqueueLog(
    { id, orderId: card.orderId, stageKey: card.stageKey, logDate: getToday(), qty, noteText: note?.trim() || null, clientCreatedAt: new Date().toISOString() },
    `${card.poNo} · ${card.stageKey}`, { photo, audio });
  triggerSync();
  return id;
}

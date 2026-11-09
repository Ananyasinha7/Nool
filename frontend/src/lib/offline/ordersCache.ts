import { api } from "../../api/client";
import type { SupOrderCard } from "../../api/types";
import { db } from "./db";

/** Stale-while-revalidate for the supervisor's list: shows the last good copy offline with its time. */
export async function loadCards(): Promise<{ cards: SupOrderCard[]; fetchedAt: number; fromCache: boolean } | null> {
  try {
    const cards = await api.supOrders();
    const fetchedAt = Date.now();
    await db.cache.put({ key: "sup", cards, fetchedAt });
    return { cards, fetchedAt, fromCache: false };
  } catch {
    const c = await db.cache.get("sup");
    return c ? { cards: c.cards, fetchedAt: c.fetchedAt, fromCache: true } : null;
  }
}
export async function readCachedCards(): Promise<{ cards: SupOrderCard[]; fetchedAt: number } | null> {
  const c = await db.cache.get("sup");
  return c ? { cards: c.cards, fetchedAt: c.fetchedAt } : null;
}

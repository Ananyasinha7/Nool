import { useEffect, useState } from "react";
import { countsOf, watchItems } from "./queue";
import { isPaused, onSyncChange } from "./sync";
import type { OutboxItem, QueueCounts } from "./types";

export function useQueue(): { items: OutboxItem[]; counts: QueueCounts } {
  const [items, setItems] = useState<OutboxItem[]>([]);
  const [paused, setPaused] = useState(isPaused());
  useEffect(() => watchItems(setItems), []);
  useEffect(() => onSyncChange(() => setPaused(isPaused())), []);
  return { items, counts: countsOf(items, paused) };
}

export function useOnline(): boolean {
  const [on, setOn] = useState(typeof navigator === "undefined" ? true : navigator.onLine);
  useEffect(() => {
    const up = () => setOn(true), down = () => setOn(false);
    window.addEventListener("online", up); window.addEventListener("offline", down);
    return () => { window.removeEventListener("online", up); window.removeEventListener("offline", down); };
  }, []);
  return on;
}

// Wires the sync engine to the browser: on submit, `online`, tab visible, app start, manual retry, timers.
// Background Sync (Workbox) is NOT used: it is Chrome-only and not needed for correctness (decision D-04).
import { raw } from "../../api/client";
import { drain, isPaused, nextDueAt, type Transport } from "./sync";

const transport: Transport = { postLog: raw.postLog, postPhoto: raw.postPhoto, postAudio: raw.postAudio };
let timer: ReturnType<typeof setTimeout> | undefined;
let started = false;

async function scheduleNext(): Promise<void> {
  if (timer) clearTimeout(timer);
  const due = await nextDueAt();
  if (due !== null && !isPaused()) timer = setTimeout(triggerSync, Math.max(500, due - Date.now()));
}

export function triggerSync(): void {
  void drain({ transport }).then(scheduleNext).catch(() => undefined);
}

export function startSync(): void {
  if (started) return;
  started = true;
  window.addEventListener("online", triggerSync);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") triggerSync(); });
  triggerSync();
}

import { useState } from "react";
import { Link } from "react-router-dom";
import { useT } from "../../i18n/provider";
import { editFailedLog, retryItem } from "../../lib/offline/queue";
import { triggerSync } from "../../lib/offline/runtime";
import { useQueue } from "../../lib/offline/useQueue";
import { BottomSheet, Button } from "../ui";

const STATE_KEY = { QUEUED: "queue.queued", SENDING: "queue.sending", SENT: "queue.sent", FAILED: "queue.failedChip" } as const;

/** Every queued item with its state; a failed item never disappears (Doc2 section 7). */
export function QueueSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const t = useT();
  const { items, counts } = useQueue();
  const [editing, setEditing] = useState<string | null>(null);
  const [qty, setQty] = useState("");
  const typeKey = { log: "", photo: ` · ${t("queue.photoItem")}`, audio: ` · ${t("queue.voiceItem")}` } as const;
  return (
    <BottomSheet open={open} onClose={onClose} title={t("queue.sheetTitle")}>
      {counts.paused && (
        <p role="alert" className="mb-3 rounded bg-amber-bg p-3 text-amber-text">
          {t("sup.signInAgain", { n: counts.queued })} <Link to="/login" className="font-semibold underline">{t("auth.signIn")}</Link>
        </p>
      )}
      {items.length === 0 ? <p className="py-6 text-ink-2">{t("queue.empty")}</p> : (
        <ul className="flex flex-col divide-y divide-line">
          {[...items].reverse().map((i) => (
            <li key={i.id} className="flex flex-col gap-2 py-3">
              <div className="flex items-center justify-between gap-3">
                <span className="min-w-0 truncate">{i.label}{typeKey[i.type]}{i.log ? ` · ${i.log.qty}` : ""}</span>
                <span className={i.state === "FAILED" ? "font-semibold text-red" : i.state === "SENT" ? "text-green" : "text-ink-2"}>{t(STATE_KEY[i.state])}</span>
              </div>
              {i.state === "FAILED" && (
                <>
                  {i.lastError && <p className="text-[13px] text-ink-2">{i.lastError}</p>}
                  {editing === i.id ? (
                    <div className="flex gap-2">
                      <input inputMode="numeric" aria-label={t("sup.todayCount")} className="min-h-[48px] flex-1 rounded border border-field px-3" value={qty} onChange={(e) => setQty(e.target.value.replace(/\D/g, ""))} />
                      <Button sup onClick={async () => { await editFailedLog(i.id, { qty: Number(qty) }); setEditing(null); triggerSync(); }}>{t("sup.send")}</Button>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <Button variant="secondary" className="min-h-[48px] flex-1" onClick={async () => { await retryItem(i.id); triggerSync(); }}>{t("common.retry")}</Button>
                      {i.type === "log" && <Button variant="ghost" className="min-h-[48px]" onClick={() => { setEditing(i.id); setQty(String(i.log?.qty ?? "")); }}>{t("queue.edit")}</Button>}
                    </div>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </BottomSheet>
  );
}

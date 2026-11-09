import { useState } from "react";
import { useT } from "../../i18n/provider";
import { useQueue } from "../../lib/offline/useQueue";
import { QueueSheet } from "./QueueSheet";

/** Offline queue state, always visible on S-6 and S-7 (Doc2 C-12). */
export function QueueChip() {
  const t = useT();
  const { counts } = useQueue();
  const [open, setOpen] = useState(false);
  let content;
  if (counts.failed > 0) content = <span className="font-semibold text-red">{t("queue.failedChip")} {counts.failed} · {t("common.retry")}</span>;
  else if (counts.sending > 0) content = <span>{t("queue.sending")}</span>;
  else if (counts.queued > 0) content = <span className="font-semibold">{t("queue.queued")} {counts.queued}</span>;
  else content = <span aria-label={t("queue.allSent")} className="text-green">●</span>;
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} aria-live="polite" className="inline-flex min-h-[48px] min-w-[48px] items-center justify-center px-2">{content}</button>
      <QueueSheet open={open} onClose={() => setOpen(false)} />
    </>
  );
}

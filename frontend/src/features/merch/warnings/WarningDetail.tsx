import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, errorKey } from "../../../api/client";
import type { EditableCategory, WarningView } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { Button, MathsPanel, StatusBadge, useToast } from "../../../components/ui";
import { NoteCompare } from "../order/NoteCompare";
import { BuyerPreview } from "./BuyerPreview";
import { buyerText } from "./buyerText";

interface Props { w: WarningView; onDone: () => void; onBack: () => void }

export function WarningDetail({ w, onDone, onBack }: Props) {
  const { t } = useI18n();
  const toast = useToast();
  const navigate = useNavigate();
  const order = useAsync(() => api.order(w.orderId), [w.orderId]);
  const initial = w.note && w.note.category !== "NEEDS_REVIEW" ? (w.note.category as EditableCategory) : "";
  const [cat, setCat] = useState<EditableCategory | "">(initial);
  const [busy, setBusy] = useState<"confirm" | "dismiss" | null>(null);
  const needsReview = !w.note || w.note.needsReview;
  const text = buyerText(cat || "NEEDS_REVIEW", w.snapshot.shipSlipDays);

  async function confirm() {
    if (!cat) return;
    setBusy("confirm");
    try {
      await api.confirmWarning(w.id, cat);
      const buyer = order.data?.buyerName ?? "";
      toast.show(t("warn.sentMock", { buyer }), { label: t("warn.viewOutbox"), onClick: () => navigate("/outbox") });
      onDone();
    } catch (e) { toast.show(t(errorKey(e))); } finally { setBusy(null); }
  }
  async function dismiss() {
    setBusy("dismiss");
    try { await api.dismissWarning(w.id); toast.show(t("warn.dismissed")); onDone(); }
    catch (e) { toast.show(t(errorKey(e))); } finally { setBusy(null); }
  }

  return (
    <div className="flex flex-col gap-5">
      <button className="inline-flex min-h-[44px] items-center self-start text-ink-2 lg:hidden" onClick={onBack}>← {t("merch.warnings")}</button>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-title"><Link to={`/orders/${w.orderId}`} className="underline-offset-4 hover:underline">{w.poNo}</Link></h2>
        <StatusBadge health={w.health} />
      </div>
      <section aria-label={t("warn.maths")} className="border-y border-line py-4">
        <p className="mb-2 text-label text-ink-3">{t("warn.maths")}</p>
        <MathsPanel h={w.snapshot} showRecovery={false} />
      </section>
      {w.note ? (
        <NoteCompare note={w.note} value={cat} highlight={needsReview && !cat} onCategory={setCat} />
      ) : (
        <div className="flex flex-col gap-2">
          <p className="text-ink-2">{t("warn.noNote")}</p>
          <NoteCompare note={{ id: "", originalText: "—", lang: "en", translationEn: "—", category: "NEEDS_REVIEW", confidence: null, source: "RULE", needsReview: true }} value={cat} highlight={!cat} onCategory={setCat} />
        </div>
      )}
      {needsReview && !cat && <p role="status" className="text-[13px] text-ink-2">{t("warn.pickCategory")}</p>}
      <BuyerPreview text={text} />
      <div className="flex flex-wrap gap-3">
        <Button disabled={!cat || busy === "dismiss"} loading={busy === "confirm"} onClick={confirm}>{t("warn.confirm")}</Button>
        <Button variant="secondary" disabled={busy === "confirm"} loading={busy === "dismiss"} onClick={dismiss}>{t("warn.dismiss")}</Button>
      </div>
    </div>
  );
}

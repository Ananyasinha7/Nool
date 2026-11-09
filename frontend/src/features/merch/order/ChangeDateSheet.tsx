import { useState } from "react";
import { api, ApiException, errorKey } from "../../../api/client";
import type { OrderDetail, ReasonCode } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { BottomSheet, Button, FormField, Select, TextInput, inputCls, useToast } from "../../../components/ui";

const REASONS: ReasonCode[] = ["BUYER_REQUEST", "MATERIAL_DELAY", "CAPACITY", "OTHER"];

/** A date change needs a reason and is append-only: submit stays disabled until valid (FR-19). */
export function ChangeDateSheet({ order, open, onClose, onSaved }: { order: OrderDetail; open: boolean; onClose: () => void; onSaved: (o: OrderDetail) => void }) {
  const { t } = useI18n();
  const toast = useToast();
  const [date, setDate] = useState("");
  const [reason, setReason] = useState<ReasonCode | "">("");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<Record<string, string>>({});
  const valid = !!date && date !== order.exFactory && !!reason && (reason !== "OTHER" || text.trim().length > 0);

  async function submit() {
    if (!valid || !reason) return;
    setBusy(true); setErr({});
    try {
      const updated = await api.changeExFactory(order.id, { toDate: date, reasonCode: reason, reasonText: text.trim() || null });
      toast.show(t("order.dateSaved"));
      setDate(""); setReason(""); setText("");
      onSaved(updated);
      onClose();
    } catch (e) {
      if (e instanceof ApiException && e.fields) setErr(e.fields); else toast.show(t(errorKey(e)));
    } finally { setBusy(false); }
  }
  return (
    <BottomSheet open={open} onClose={onClose} title={t("order.changeDate")}>
      <div className="flex flex-col gap-4">
        <FormField label={t("order.newDate")} error={err.toDate}>
          {({ id, describedBy, invalid }) => <input id={id} type="date" aria-describedby={describedBy} className={inputCls(invalid)} value={date} onChange={(e) => setDate(e.target.value)} />}
        </FormField>
        <Select label={t("order.reasonLabel")} value={reason} placeholder="—" options={REASONS.map((r) => ({ value: r, label: t(`order.reason.${r}`) }))} onChange={(v) => setReason(v as ReasonCode | "")} />
        <TextInput label={t("order.reasonText")} value={text} maxLength={300} onChange={(e) => setText(e.target.value)} error={err.reasonText} />
        <Button disabled={!valid} loading={busy} onClick={submit}>{t("common.save")}</Button>
      </div>
    </BottomSheet>
  );
}

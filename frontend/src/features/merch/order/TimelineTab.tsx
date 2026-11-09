import { useState } from "react";
import { api, errorKey } from "../../../api/client";
import type { OrderDetail } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { Timeline, useToast, type TimelineItem } from "../../../components/ui";

export function TimelineTab({ order, today, onChanged }: { order: OrderDetail; today: string; onChanged: () => void }) {
  const { t } = useI18n();
  const toast = useToast();
  const [busy, setBusy] = useState<string | null>(null);
  async function tick(m: TimelineItem) {
    if (!m.id) return;
    setBusy(m.id);
    try {
      await api.tickMilestone(m.id, m.actualDate ? null : today); // ticking is audited server-side (FR-05)
      toast.show(t("order.tickSaved"));
      onChanged();
    } catch (e) { toast.show(t(errorKey(e))); } finally { setBusy(null); }
  }
  const items: TimelineItem[] = order.milestones.map((m) => ({ id: m.id, name: m.name, plannedDate: m.plannedDate, actualDate: m.actualDate, manual: m.kind === "MANUAL" }));
  return <Timeline items={items} today={today} onTick={tick} busyId={busy} />;
}

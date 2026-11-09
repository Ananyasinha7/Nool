import { api, errorKey } from "../../../api/client";
import type { OrderDetail } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { fmtDate, fmtDateYear } from "../../../lib/format";
import { ErrorState, Skeleton } from "../../../components/ui";

/** Always shown, even when empty (Doc2 S-3): the compliance history of date changes. */
export function DateHistoryTab({ order, version }: { order: OrderDetail; version: number }) {
  const { t, lang } = useI18n();
  const ch = useAsync(() => api.orderChanges(order.id), [order.id, version]);
  if (ch.loading && !ch.data) return <Skeleton className="h-24 w-full" />;
  if (ch.error) return <ErrorState message={t(errorKey(ch.error))} onRetry={ch.reload} />;
  if (!ch.data?.length) return <p className="py-6 text-ink-2">{t("order.noChanges")}</p>;
  return (
    <ul className="flex flex-col">
      {ch.data.map((c) => (
        <li key={c.id} className="flex flex-col gap-0.5 border-b border-line py-3 last:border-b-0">
          <p className="font-medium">{fmtDate(c.fromDate, lang)} → {fmtDateYear(c.toDate, lang)}</p>
          <p className="text-ink-2">{t(`order.reason.${c.reasonCode}`)}{c.reasonText ? `: ${c.reasonText}` : ""}</p>
          <p className="text-[13px] text-ink-3">{c.changedByName} · {fmtDateYear(c.changedAt, lang)}</p>
        </li>
      ))}
    </ul>
  );
}

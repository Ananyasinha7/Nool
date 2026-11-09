import { api, errorKey } from "../../../api/client";
import type { OrderDetail } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { fmtDate, fmtNum } from "../../../lib/format";
import { EmptyState, ErrorState, Skeleton, useToast } from "../../../components/ui";
import { stageKey } from "../board/shared";
import { Sparkline } from "./Sparkline";

export function DailyOutputTab({ order }: { order: OrderDetail }) {
  const { t, lang } = useI18n();
  const toast = useToast();
  const logs = useAsync(() => api.orderLogs(order.id, 10), [order.id], `logs:${order.id}`);
  if (logs.loading && !logs.data) return <Skeleton className="h-40 w-full" />;
  if (logs.error) return <ErrorState message={t(errorKey(logs.error))} onRetry={logs.reload} />;
  const rows = Array.isArray(logs.data) ? logs.data : [];
  if (rows.length === 0) return <EmptyState text={t("order.noLogs")} />;
  const active = order.health.activeStage;
  const spark = rows.filter((r) => r.stageKey === active).map((r) => ({ date: r.logDate, qty: r.qty })).reverse().slice(-10);
  async function share(id: string, next: boolean) {
    try { await api.sharephoto(id, next); toast.show(t("common.saved")); logs.reload(); }
    catch (e) { toast.show(t(errorKey(e))); }
  }
  return (
    <div className="flex flex-col gap-4">
      <Sparkline points={spark} />
      <div className="overflow-x-auto rounded-md border border-line bg-surface">
        <table className="w-full text-left">
          <thead><tr className="border-b border-line text-label text-ink-3">
            <th className="px-3 py-2">{t("order.colDate")}</th><th className="px-3 py-2">{t("merch.colStage")}</th>
            <th className="px-3 py-2 text-right">{t("order.colQty")}</th><th className="px-3 py-2">{t("order.colBy")}</th><th className="px-3 py-2">{t("sup.photo")}</th>
          </tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-b border-line last:border-b-0">
                <td className="px-3 py-2">{fmtDate(r.logDate, lang)}</td>
                <td className="px-3 py-2 text-ink-2">{t(stageKey(r.stageKey))}</td>
                <td className="px-3 py-2 text-right font-medium">{fmtNum(r.qty)}</td>
                <td className="px-3 py-2 text-ink-2">{r.enteredBy}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap gap-2">
                    {r.photoIds.map((pid) => {
                      const shared = r.sharedPhotoIds.includes(pid);
                      return (
                        <span key={pid} className="flex items-center gap-1">
                          <img src={`/api/photos/${pid}`} alt={`${order.poNo} ${fmtDate(r.logDate, lang)}`} width={40} height={40} loading="lazy" className="h-10 w-10 rounded object-cover" />
                          <button className="min-h-[44px] px-1 text-[13px] underline" aria-pressed={shared} onClick={() => share(pid, !shared)}>
                            {shared ? t("order.photoShared") : t("order.sharePhoto")}
                          </button>
                        </span>
                      );
                    })}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

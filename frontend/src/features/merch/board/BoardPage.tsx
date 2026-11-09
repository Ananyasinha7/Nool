import { useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api, errorKey } from "../../../api/client";
import type { Health } from "../../../api/types";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { usePageTitle } from "../../../lib/usePageTitle";
import { EmptyState, ErrorState, SkeletonRows } from "../../../components/ui";
import { apiQuery, parseFilters, toParams } from "./filters";
import { FilterBar } from "./FilterBar";
import { OrderCard } from "./OrderCard";
import { OrderRow } from "./OrderRow";
import { SummaryStrip } from "./SummaryStrip";

export default function BoardPage() {
  const { t } = useI18n();
  usePageTitle(t("merch.board"));
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const filters = useMemo(() => parseFilters(params), [params]);
  const q = JSON.stringify(apiQuery(filters));
  const orders = useAsync(() => api.orders(apiQuery(filters)), [q]);
  const lookups = useAsync(() => api.lookups(), []);


  const counts = useMemo(() => {
    const c: Record<Health, number> = { RED: 0, AMBER: 0, GREEN: 0, GREY: 0 };
    for (const o of orders.data ?? []) c[o.health.health]++;
    return c;
  }, [orders.data]);
  const filtered = (orders.data ?? []).filter((o) => !filters.status || o.health.health === filters.status);
  const SEVERITY: Record<string, number> = { RED: 0, AMBER: 1, GREEN: 2, GREY: 3 };
  const shown = [...filtered].sort((a, b) => {
    switch (filters.sort) {
      case "exFactory": return a.exFactory.localeCompare(b.exFactory);
      case "qty": return b.qty - a.qty;
      case "po": return a.poNo.localeCompare(b.poNo);
      default: return (SEVERITY[a.health.health] ?? 3) - (SEVERITY[b.health.health] ?? 3);
    }
  });
  const change = (f: typeof filters) => setParams(toParams(f), { replace: true });

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-end justify-between gap-4">
        <h1 className="text-title">{t("merch.orders")}</h1>
        <a href={api.exportUrl(filters.week)} download className="inline-flex min-h-[44px] items-center text-ink-2 underline">{t("merch.exportWeekly")} ↓</a>
      </div>
      <SummaryStrip counts={counts} active={filters.status} onPick={(status) => change({ ...filters, status })} />
      <FilterBar filters={filters} lookups={lookups.data} onChange={change} onClear={() => setParams({}, { replace: true })} />
      {orders.loading && !orders.data ? <SkeletonRows n={6} />
        : orders.error ? <ErrorState message={t(errorKey(orders.error))} onRetry={orders.reload} />
        : shown.length === 0 ? (
          Object.values(filters).some(Boolean)
            ? <EmptyState text={t("merch.emptyFiltered")} actionLabel={t("common.clearFilters")} onAction={() => setParams({}, { replace: true })} />
            : <EmptyState text={t("merch.empty")} actionLabel={t("merch.newOrder")} onAction={() => nav("/orders/new")} />
        ) : (
          <>
            <p className="hidden text-[13px] text-ink-3 md:block">■ {t("merch.colProgress")} · ▸ {t("common.legendTick")} · ◇ {t("common.legendRate")}</p>
            <div className="hidden overflow-hidden rounded-lg border border-line bg-surface shadow-xs md:block">
              <div className="grid grid-cols-[150px_1.5fr_90px_1.2fr_75px_1.4fr] gap-4 border-b border-line bg-[#F5F3EC] px-4 py-2.5 text-[11px] font-semibold tracking-wider text-ink-3 uppercase">
                <span>{t("merch.status")}</span><span>{t("merch.colOrder")}</span><span>{t("merch.colStage")}</span>
                <span>{t("merch.colProgress")}</span><span>{t("merch.colShip")}</span><span>{t("merch.colProjection")}</span>
              </div>
              {shown.map((o) => <OrderRow key={o.id} o={o} />)}
            </div>
            <div className="flex flex-col gap-3 md:hidden">{shown.map((o) => <OrderCard key={o.id} o={o} />)}</div>
          </>
        )}
    </div>
  );
}

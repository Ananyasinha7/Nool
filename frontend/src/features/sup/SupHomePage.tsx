import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/client";
import type { SupOrderCard } from "../../api/types";
import { InstallCard } from "../../components/sup/InstallCard";
import { OrderCardSup } from "../../components/sup/OrderCardSup";
import { SupHeader } from "../../components/sup/SupHeader";
import { EmptyState, SkeletonRows } from "../../components/ui";
import { useI18n } from "../../i18n/provider";
import { useAuth } from "../../lib/auth";
import { loadCards, readCachedCards } from "../../lib/offline/ordersCache";
import { startSync } from "../../lib/offline/runtime";
import { useQueue } from "../../lib/offline/useQueue";
import { getToday, setToday } from "../../lib/today";
import { usePageTitle } from "../../lib/usePageTitle";

export default function SupHomePage() {
  const { t } = useI18n();
  usePageTitle(t("sup.myOrders"));
  const { me } = useAuth();
  const { items, counts } = useQueue();
  const [cards, setCards] = useState<SupOrderCard[] | null>(null);
  const [refreshed, setRefreshed] = useState<number | null>(null);
  const [stale, setStale] = useState(false);
  const [query, setQuery] = useState("");
  const [stageFilter, setStageFilter] = useState("");

  useEffect(() => {
    startSync();
    let alive = true;
    void readCachedCards().then((c) => { if (alive && c) { setCards((x) => x ?? c.cards); setRefreshed((x) => x ?? c.fetchedAt); setStale(true); } });
    void api.healthz().then((h) => setToday(h.today)).catch(() => undefined); // the server's date (demo clock aware)
    void loadCards().then((r) => { if (!alive) return; if (r) { setCards(r.cards); setRefreshed(r.fetchedAt); setStale(r.fromCache); } else setCards((x) => x ?? []); });
    return () => { alive = false; };
  }, []);

  const today = getToday();
  const entered = useMemo(() => {
    const m = new Map<string, { qty: number; state: (typeof items)[number]["state"] }>();
    for (const i of items) {
      if (i.log) {
        m.set(`${i.log.orderId}|${i.log.stageKey}`, { qty: i.log.qty, state: i.state });
      }
    }
    return m;
  }, [items]);

  // Re-fetch fresh server cards whenever outbox finishes syncing, page refocuses, or periodically across devices
  useEffect(() => {
    const refresh = () => {
      void loadCards().then((r) => { if (r) { setCards(r.cards); setRefreshed(r.fetchedAt); } });
    };
    if (items.some((i) => i.state === "SENT")) {
      refresh();
    }
    const timer = setInterval(refresh, 8000); // 8s auto-sync between phone & laptop
    window.addEventListener("focus", refresh);
    const onVis = () => { if (document.visibilityState === "visible") refresh(); };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      clearInterval(timer);
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", onVis);
    };
  }, [items]);

  const q = query.trim().toLowerCase();
  const stages = useMemo(() => cards ? [...new Set(cards.map((c) => c.stageKey))] : [], [cards]);
  const visible = useMemo(() =>
    cards === null ? null : cards.filter((c) => {
      const matchStage = !stageFilter || c.stageKey === stageFilter;
      const matchQ = !q || c.poNo.toLowerCase().includes(q) || c.stageKey.toLowerCase().includes(q) || c.style.toLowerCase().includes(q);
      return matchStage && matchQ;
    }),
  [cards, q, stageFilter]);

  const time = refreshed ? new Date(refreshed).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }) : "";
  return (
    <>
      <SupHeader title={`${t("sup.hello")}, ${me?.displayName ?? ""}`} />
      <main className="mx-auto flex w-full max-w-page flex-1 flex-col gap-4 px-4 py-4 md:px-6 md:py-6">
        {counts.paused && (
          <p role="alert" className="rounded bg-amber-bg p-3 text-amber-text">{t("sup.signInAgain", { n: counts.queued })} <Link to="/login" className="font-semibold underline">{t("auth.signIn")}</Link></p>
        )}
        <h2 className="text-heading">{t("sup.myOrders")}</h2>
        {/* Search + filter bar */}
        {cards !== null && cards.length > 0 && (
          <div className="flex flex-col gap-2">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by PO, style or stage…"
              aria-label="Filter orders"
              className="w-full rounded-md border border-line bg-surface px-3 py-2.5 text-[14px] text-ink placeholder:text-ink-3 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20"
            />
            <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by stage">
              <button
                type="button"
                onClick={() => setStageFilter("")}
                className={`rounded-full border px-3 py-1 text-[12px] font-medium transition-colors ${!stageFilter ? "border-ink bg-ink text-paper" : "border-line bg-surface text-ink-2 hover:bg-paper"}`}
              >All</button>
              {stages.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setStageFilter(stageFilter === s ? "" : s)}
                  className={`rounded-full border px-3 py-1 text-[12px] font-medium capitalize transition-colors ${stageFilter === s ? "border-ink bg-ink text-paper" : "border-line bg-surface text-ink-2 hover:bg-paper"}`}
                >
                  {t(`stage.${s.toLowerCase()}`)}
                </button>
              ))}
            </div>
          </div>
        )}
        {visible === null ? <SkeletonRows n={3} />
          : visible.length === 0 ? <EmptyState text={q ? "No orders match your search." : t("sup.noOrders")} />
          : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {visible.map((c) => {
                const e = entered.get(`${c.orderId}|${c.stageKey}`);
                const todayVal = e && (e.state === "QUEUED" || e.state === "SENDING") ? e.qty : (c.todayQty ?? e?.qty ?? null);
                return <OrderCardSup key={`${c.orderId}-${c.stageKey}`} c={c} entered={todayVal} mark={e ? e.state : null} />;
              })}
            </div>
          )}
        {stale && time && <p className="text-[13px] text-ink-3">{t("sup.lastRefreshed")}: {time}</p>}
        <div className="max-w-md">
          <InstallCard />
        </div>
      </main>
    </>
  );
}

import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, errorKey } from "../../../api/client";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { useToday } from "../../../lib/today";
import { usePageTitle } from "../../../lib/usePageTitle";
import { ErrorState, Skeleton } from "../../../components/ui";
import { ChangeDateSheet } from "./ChangeDateSheet";
import { DailyOutputTab } from "./DailyOutputTab";
import { DateHistoryTab } from "./DateHistoryTab";
import { IssuesTab } from "./IssuesTab";
import { MathsSection } from "./MathsSection";
import { OrderHeader } from "./OrderHeader";
import { Tabs } from "./Tabs";
import { TimelineTab } from "./TimelineTab";

export default function OrderPage() {
  const { id = "" } = useParams();
  const { t } = useI18n();
  const order = useAsync(() => api.order(id), [id]);
  const o = order.data;
  usePageTitle(o?.poNo ? `${o.poNo} (${o.style})` : t("merch.orders"));
  const [tab, setTab] = useState("timeline");
  const [sheet, setSheet] = useState(false);
  const [version, setVersion] = useState(0);
  const today = useToday();

  if (order.loading && !o) return <div className="flex flex-col gap-4"><Skeleton className="h-10 w-2/3" /><Skeleton className="h-32 w-full" /><Skeleton className="h-48 w-full" /></div>;
  if (order.error || !o) return <ErrorState message={t(errorKey(order.error))} onRetry={order.reload} />;

  const stage = o.health.activeStage ?? "PACKING";
  const unitName = o.assignments.find((a) => a.stageKey === stage)?.unitName ?? o.assignments[0]?.unitName ?? "";
  return (
    <div className="flex flex-col gap-5">
      <OrderHeader o={o} unitName={unitName} onChangeDate={() => setSheet(true)} />
      <MathsSection h={o.health} />
      {o.openWarning && (
        <Link to="/warnings" className="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-amber-text hover:bg-amber-100">
          <span className="font-medium">{t("order.pendingWarning")}</span>
          <span className="ml-auto text-[13px] underline">{t("order.reviewWarning")}</span>
        </Link>
      )}
      <Tabs active={tab} onChange={setTab} tabs={[
        { id: "timeline", label: t("order.timeline") }, { id: "output", label: t("order.output") },
        { id: "issues", label: t("order.issues") }, { id: "history", label: t("order.history") },
      ]}>
        {tab === "timeline" && <TimelineTab order={o} today={today} onChanged={order.reload} />}
        {tab === "output" && <DailyOutputTab order={o} />}
        {tab === "issues" && <IssuesTab order={o} />}
        {tab === "history" && <DateHistoryTab order={o} version={version} />}
      </Tabs>
      <ChangeDateSheet order={o} open={sheet} onClose={() => setSheet(false)} onSaved={(u) => { order.setData(u); setVersion((v) => v + 1); }} />
    </div>
  );
}

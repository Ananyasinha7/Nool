import { useParams } from "react-router-dom";
import { api, ApiException, errorKey } from "../../api/client";
import { BuyerHeader } from "../../components/buyer/BuyerHeader";
import { BuyerTimeline } from "../../components/buyer/BuyerTimeline";
import { DateHistory } from "../../components/buyer/DateHistory";
import { DelayNotice } from "../../components/buyer/DelayNotice";
import { PhotoGrid } from "../../components/buyer/PhotoGrid";
import { ErrorState, ProgressBar, Skeleton } from "../../components/ui";
import { useI18n } from "../../i18n/provider";
import { useAuth } from "../../lib/auth";
import { fmtDateYear, fmtNum } from "../../lib/format";
import { useAsync } from "../../lib/useAsync";
import { usePageTitle } from "../../lib/usePageTitle";
import InvalidLinkPage from "./InvalidLinkPage";

export default function BuyerOrderPage() {
  const { id = "" } = useParams();
  const { t, lang } = useI18n();
  const { me } = useAuth();
  const order = useAsync(() => api.buyerOrder(id), [id]);
  if (order.error instanceof ApiException && order.error.status === 401) return <InvalidLinkPage />;
  const o = order.data;
  usePageTitle(o?.poNo ? `${o.poNo} (${o.style})` : t("buyer.header"));
  const h = (label: string) => <h2 className="mb-2 text-heading">{label}</h2>;
  return (
    <>
      <BuyerHeader company={me?.buyerName ?? ""} crumb={{ to: "/b", label: t("buyer.header") }} />
      <main className="mx-auto flex max-w-page flex-col gap-8 px-4 py-6 md:px-6">
        {order.loading && !o ? <><Skeleton className="h-10 w-1/2" /><Skeleton className="h-40 w-full" /></>
          : order.error || !o ? <ErrorState message={t(errorKey(order.error))} onRetry={order.reload} />
          : (
            <>
              <section className="flex flex-col gap-2">
                <h1 className="text-title">{o.poNo} <span className="text-ink-2">{o.style}, {o.colour}</span></h1>
                <p className="text-ink-2">{fmtNum(o.qty)} {t("buyer.qty")} · {t("buyer.shipDate")} {fmtDateYear(o.exFactory, lang)}</p>
                <ProgressBar neutral done={o.progressPct} qty={100} label={t("buyer.progress")} />
                <p className="text-[13px] text-ink-2 font-medium">
                  {o.currentStage ? `${t(`stage.${o.currentStage.toLowerCase()}`)} · ` : ""}
                  {o.progressPct}% · {o.delayNotice ? `+${o.delayNotice.shipSlipDays} ${t("common.days")}` : t("common.onTime")} ({t("buyer.shipDate")} {fmtDateYear(o.exFactory, lang)})
                </p>
                {o.delayNotice && <DelayNotice n={o.delayNotice} />}
                <a href={api.exportUrl()} download className="inline-flex min-h-[44px] items-center self-start text-ink-2 underline">{t("buyer.download")}</a>
              </section>
              <section>{h(t("buyer.timeline"))}<BuyerTimeline items={o.milestones} /></section>
              <section>{h(t("buyer.photos"))}<PhotoGrid photos={o.photos} po={o.poNo} /></section>
              <section>{h(t("buyer.history"))}<DateHistory rows={o.dateHistory} /></section>
            </>
          )}
      </main>
    </>
  );
}

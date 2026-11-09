import { Link } from "react-router-dom";
import { useI18n } from "../../../i18n/provider";
import { fmtDate, fmtNum } from "../../../lib/format";
import type { OrderSummary } from "../../../api/types";
import { ProgressBar, StatusBadge } from "../../../components/ui";
import { projectionKeys, stageKey } from "./shared";

/** Mobile card: badge on the first line, projection sentence below (Doc2 S-2 mobile). Never a scrolling table. */
export function OrderCard({ o }: { o: OrderSummary }) {
  const { t, lang } = useI18n();
  const h = o.health;
  const maths = h.overdue || h.requiredPerDay === null ? t("merch.stageOverdue")
    : t("merch.needMaking", { need: fmtNum(h.requiredPerDay), making: fmtNum(h.actualPerDay) });
  const { flagKey, flagN } = projectionKeys(o);
  const slip = h.stageSlipDays > 1 ? t("merch.slipDays", { n: h.stageSlipDays }) : h.stageSlipDays === 1 ? t("merch.slipDay") : t("common.onTime");
  return (
    <Link to={`/orders/${o.id}`} className="flex flex-col gap-2.5 rounded-lg border border-line bg-surface p-4 shadow-xs transition-all duration-150 hover:border-line-strong hover:shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <StatusBadge health={h.health} />
        <span className="text-ink-2">{fmtDate(o.exFactory, lang)}</span>
      </div>
      <div>
        <p className="font-semibold">{o.poNo}</p>
        <p className="text-ink-2">{o.style}, {o.colour}</p>
        <p className="text-[13px] text-ink-3">{o.buyerName} · {o.unitName} · {t(stageKey(h.activeStage))}</p>
      </div>
      <ProgressBar done={h.done} qty={h.qty} health={h.health} tickAt={h.projectedAtDeadline} label={o.poNo} />
      <p className="text-ink-2">{slip} {t(stageKey(h.activeStage))} · {maths}</p>
      <p className="text-[13px] text-ink-3">{h.shipSlipDays > 0 ? t("common.shipImpactSlip", { n: h.shipSlipDays }) : t("common.shipImpactSafe")}</p>
      {o.openWarning && <span className="inline-flex items-center rounded bg-amber-50 px-2 py-0.5 text-[12px] font-medium text-amber-text">{t("common.warningWaiting")}</span>}
      {flagKey && <p className="text-[13px] text-ink-3">{t(flagKey, { n: flagN })}</p>}
    </Link>
  );
}

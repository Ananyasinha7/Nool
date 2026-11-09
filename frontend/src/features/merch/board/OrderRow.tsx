import { Link } from "react-router-dom";
import { useI18n } from "../../../i18n/provider";
import { fmtDate, fmtNum } from "../../../lib/format";
import type { OrderSummary } from "../../../api/types";
import { ProgressBar, StatusBadge } from "../../../components/ui";
import { projectionKeys, stageKey } from "./shared";

function useProjection(o: OrderSummary) {
  const { t } = useI18n();
  const h = o.health;
  const slip = h.stageSlipDays > 1 ? t("merch.slipDays", { n: h.stageSlipDays })
    : h.stageSlipDays === 1 ? t("merch.slipDay") : t("common.onTime");
  const maths = h.overdue || h.requiredPerDay === null ? t("merch.stageOverdue")
    : t("merch.needMaking", { need: fmtNum(h.requiredPerDay), making: fmtNum(h.actualPerDay) });
  const { flagKey, flagN } = projectionKeys(o);
  return { slip, maths, flag: flagKey ? t(flagKey, { n: flagN }) : null, late: h.health === "RED" };
}

/** Desktop table row (Doc2 C-08). The row stays white; only the status word is coloured. */
export function OrderRow({ o }: { o: OrderSummary }) {
  const { t, lang } = useI18n();
  const p = useProjection(o);
  const h = o.health;
  return (
    <Link to={`/orders/${o.id}`} className="grid grid-cols-[150px_1.5fr_90px_1.2fr_75px_1.4fr] items-start gap-4 border-b border-line bg-surface px-4 py-3.5 transition-colors duration-150 hover:bg-[#FAF8F4] last:border-b-0">
      <div className="min-w-0"><StatusBadge health={h.health} /></div>
      <div className="min-w-0">
        <p className="font-semibold">{o.poNo}</p>
        <p className="truncate text-ink-2">{o.style}, {o.colour}</p>
        <p className="text-[13px] text-ink-3">{o.buyerName} · {o.unitName}</p>
      </div>
      <p className="text-ink-2">{t(stageKey(h.activeStage))}</p>
      <div className="flex flex-col gap-1.5 pt-1.5">
        <ProgressBar done={h.done} qty={h.qty} health={h.health} tickAt={h.projectedAtDeadline} label={o.poNo} />
        <p className="text-[13px] text-ink-2">{fmtNum(h.done)} / {fmtNum(h.qty)}</p>
      </div>
      <p className="text-ink-2">{fmtDate(o.exFactory, lang)}</p>
      <div>
        <p className={p.late ? "font-medium text-red" : h.health === "AMBER" ? "font-medium text-amber-text" : "text-ink-2"}>{p.slip} {t(stageKey(h.activeStage))}</p>
        <p className="text-[13px] text-ink-2">{p.maths}</p>
        <p className="text-[13px] text-ink-3">{h.shipSlipDays > 0 ? t("common.shipImpactSlip", { n: h.shipSlipDays }) : t("common.shipImpactSafe")}</p>
        {p.flag && <p className="text-[13px] text-ink-3">{p.flag}</p>}
        {o.openWarning && <span className="mt-1 inline-flex items-center rounded bg-amber-50 px-2 py-0.5 text-[12px] font-medium text-amber-text">{t("common.warningWaiting")}</span>}
      </div>
    </Link>
  );
}

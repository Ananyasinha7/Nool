import { useI18n } from "../../i18n/provider";
import { fmtDate, fmtNum } from "../../lib/format";
import type { OrderHealth } from "../../api/types";

/** The product's signature element: the maths in plain words (Doc2 C-09, FR-13). */
export function MathsPanel({ h, showRecovery = true }: { h: OrderHealth; showRecovery?: boolean }) {
  const { t, lang } = useI18n();
  if (h.activeStage === null) return <p className="text-heading">{t("stage.done")}</p>;
  const line1 = h.overdue || h.requiredPerDay === null
    ? t("order.overdue", { rem: fmtNum(h.remaining) })
    : t("order.maths", { need: fmtNum(h.requiredPerDay), making: fmtNum(h.actualPerDay), days: h.workingDaysLeft });
  const line2 = h.stageSlipDays > 0
    ? t("order.projected", { date: fmtDate(h.projectedFinish, lang), slip: h.stageSlipDays })
    : t("order.projectedOk", { date: fmtDate(h.projectedFinish, lang) });
  return (
    <div className="flex flex-col gap-1">
      <p className="text-heading text-ink">{line1}</p>
      <p className="text-ink-2">{line2}</p>
      {h.shipSlipDays > 0 && <p className="text-ink-2">{t("order.shipImpact", { date: fmtDate(h.projectedShipDate, lang), slip: h.shipSlipDays })}</p>}
      {showRecovery && h.recoveryPerDay > 0 && !h.overdue && <p className="text-ink-2">{t("order.recovery", { n: fmtNum(h.recoveryPerDay) })}</p>}
      {h.lowConfidence && <p className="text-[13px] text-ink-3">{t("order.noUpdates")}</p>}
    </div>
  );
}

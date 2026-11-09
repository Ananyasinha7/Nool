import { Link } from "react-router-dom";
import { useI18n } from "../../i18n/provider";
import { fmtDate, fmtNum } from "../../lib/format";
import type { BuyerOrderView } from "../../api/types";
import { ProgressBar } from "../ui";
import { DelayNotice } from "./DelayNotice";

export function BuyerOrderRow({ o }: { o: BuyerOrderView }) {
  const { t, lang } = useI18n();
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-line bg-surface p-5 shadow-xs transition-all duration-150 hover:border-line-strong hover:shadow-sm">
      <Link to={`/b/orders/${o.id}`} className="flex flex-col gap-2.5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="font-semibold text-heading text-ink">{o.poNo}</p>
            <p className="text-ink-2 text-[14px] leading-snug">{o.style}, {o.colour}</p>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="font-medium text-ink whitespace-nowrap">{fmtNum(o.qty)} {t("buyer.qty")}</p>
            <p className="text-ink-2 text-[13px] whitespace-nowrap">{t("buyer.shipDate")} {fmtDate(o.exFactory, lang)}</p>
          </div>
        </div>
        <ProgressBar neutral done={o.progressPct} qty={100} label={`${o.poNo} ${t("buyer.progress")}`} />
        <p className="text-[13px] text-ink-2 font-medium">{o.progressPct}%{o.currentStage ? ` · ${t(`stage.${o.currentStage.toLowerCase()}`)}` : ""}</p>
      </Link>
      {o.delayNotice && <DelayNotice n={o.delayNotice} />}
    </div>
  );
}

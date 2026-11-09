import { Link } from "react-router-dom";
import { useT } from "../../i18n/provider";
import { fmtNum } from "../../lib/format";
import type { SupOrderCard } from "../../api/types";
import type { ItemState } from "../../lib/offline/types";

const MARK: Record<ItemState, string> = { QUEUED: "⏱", SENDING: "↑", SENT: "✓", FAILED: "!" };

/** No status colours on the floor (BR-08): the order, stage, today's need and what was entered. */
export function OrderCardSup({ c, entered, mark }: { c: SupOrderCard; entered: number | null; mark: ItemState | null }) {
  const t = useT();
  const remainingToday = Math.max(0, c.neededToday - (entered ?? 0));

  return (
    <div className="flex flex-col justify-between gap-4 rounded-lg border border-line bg-surface p-5 shadow-xs transition-shadow duration-150 hover:shadow-sm">
      <div className="flex flex-col gap-2.5">
        <p className="text-heading font-semibold text-ink">{c.poNo}</p>
        <p className="text-ink-2 font-medium text-[14px]">{c.style} · {t(`stage.${c.stageKey.toLowerCase()}`)}</p>
        <div className="grid grid-cols-3 gap-2 pt-1 text-[13px] sm:text-[14px]">
          <div>
            <span className="text-ink-3 block text-[11px] font-medium leading-tight">{t("sup.needed")}</span>
            <b className="text-heading font-semibold text-ink text-[15px] sm:text-[16px]">{fmtNum(c.neededToday)}</b>
          </div>
          <div>
            <span className="text-ink-3 block text-[11px] font-medium leading-tight">{t("common.today")}</span>
            <b className="text-heading font-semibold text-ink text-[15px] sm:text-[16px]">
              {entered === null ? "—" : fmtNum(entered)}
            </b>
            {mark && <span aria-hidden="true" className="ml-1 text-[12px] text-ink-3 font-semibold">{MARK[mark]}</span>}
          </div>
          <div>
            <span className="text-ink-3 block text-[11px] font-medium leading-tight">{t("sup.remainingToday")}</span>
            <b className={`text-heading font-semibold text-[15px] sm:text-[16px] ${remainingToday === 0 && entered !== null ? "text-green" : "text-ink"}`}>
              {fmtNum(remainingToday)}
            </b>
          </div>
        </div>
      </div>
      <Link to={`/s/update/${c.orderId}/${c.stageKey}`} className="press mt-2 flex min-h-[56px] items-center justify-center rounded-md border border-ink bg-ink px-4 text-[18px] font-semibold text-paper shadow-xs hover:bg-[#252E29]">
        {t("sup.addCount")}
      </Link>
    </div>
  );
}

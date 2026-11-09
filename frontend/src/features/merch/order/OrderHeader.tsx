import { Link } from "react-router-dom";
import { useI18n } from "../../../i18n/provider";
import { fmtDateYear, fmtNum } from "../../../lib/format";
import type { OrderDetail } from "../../../api/types";
import { Button, StatusBadge } from "../../../components/ui";

export function OrderHeader({ o, unitName, onChangeDate }: { o: OrderDetail; unitName: string; onChangeDate: () => void }) {
  const { t, lang } = useI18n();
  return (
    <div className="flex flex-col gap-2">
      <Link to="/board" className="inline-flex min-h-[44px] items-center text-ink-2">← {t("merch.board")}</Link>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-title">{o.poNo} <span className="text-ink-2">{o.style}, {o.colour}</span></h1>
        </div>
        <StatusBadge health={o.health.health} />
      </div>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-ink-2">
        <span>{o.buyerName}</span><span aria-hidden="true">·</span><span>{unitName}</span><span aria-hidden="true">·</span>
        <span>{fmtNum(o.qty)} {t("common.pcs")}</span><span aria-hidden="true">·</span>
        <span>{t("order.exFactory")} {fmtDateYear(o.exFactory, lang)}</span>
        <Button variant="secondary" className="min-h-[36px] px-3" onClick={onChangeDate}>{t("order.changeDate")}</Button>
      </div>
    </div>
  );
}

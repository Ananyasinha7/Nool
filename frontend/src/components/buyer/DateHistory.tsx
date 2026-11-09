import { useI18n } from "../../i18n/provider";
import { fmtDate, fmtDateYear } from "../../lib/format";
import type { BuyerOrderDetail } from "../../api/types";

/** Chronological, with reason and the merchandiser's name (FR-20). Always shown, even when empty. */
export function DateHistory({ rows }: { rows: BuyerOrderDetail["dateHistory"] }) {
  const { t, lang } = useI18n();
  if (rows.length === 0) return <p className="text-ink-2">{t("buyer.noChanges")}</p>;
  return (
    <div className="overflow-x-auto rounded-md border border-line bg-surface">
      <table className="w-full text-left">
        <thead><tr className="border-b border-line text-label text-ink-3">
          <th className="px-3 py-2">{t("order.colDate")}</th><th className="px-3 py-2">{t("order.from")}</th><th className="px-3 py-2">{t("order.to")}</th><th className="px-3 py-2">{t("order.reasonLabel")}</th><th className="px-3 py-2">{t("order.by")}</th>
        </tr></thead>
        <tbody>{rows.map((r, i) => (
          <tr key={i} className="border-b border-line last:border-b-0">
            <td className="px-3 py-2">{fmtDateYear(r.changedAt, lang)}</td><td className="px-3 py-2">{fmtDate(r.fromDate, lang)}</td>
            <td className="px-3 py-2">{fmtDate(r.toDate, lang)}</td><td className="px-3 py-2 text-ink-2">{r.reason}</td><td className="px-3 py-2 text-ink-2">{r.changedBy}</td>
          </tr>))}</tbody>
      </table>
    </div>
  );
}

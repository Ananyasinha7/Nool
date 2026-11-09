import { useI18n } from "../../i18n/provider";
import { fmtDate } from "../../lib/format";
import { Button } from "./Button";

export interface TimelineItem { id?: string; name: string; plannedDate: string; actualDate: string | null; manual?: boolean }
interface Props { items: TimelineItem[]; today: string; onTick?: (item: TimelineItem) => void; busyId?: string | null }

/** Vertical milestone list: planned date, actual date, state (Doc2 C-10). */
export function Timeline({ items, today, onTick, busyId }: Props) {
  const { t, lang } = useI18n();
  return (
    <ol className="relative flex flex-col">
      {items.map((m, idx) => {
        const done = m.actualDate !== null;
        const overdue = !done && m.plannedDate < today;
        const isLast = idx === items.length - 1;
        return (
          <li key={m.id ?? m.name} className="relative flex items-start gap-3.5 pb-5 last:pb-1">
            {!isLast && (
              <div
                aria-hidden="true"
                className={`absolute left-[9px] top-5 -bottom-1 w-[1.5px] ${
                  done ? "bg-[#CDE3D5]" : "bg-line"
                }`}
              />
            )}
            <span
              aria-hidden="true"
              className={`relative z-10 mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                done
                  ? "bg-green-bg text-green border border-[#CDE3D5]"
                  : overdue
                  ? "bg-red-bg text-red border border-[#F3D7CF]"
                  : "bg-surface text-ink-3 border border-line"
              }`}
            >
              {done ? "✓" : overdue ? "!" : "○"}
            </span>
            <div className="min-w-0 flex-1 pt-0.5">
              <p className="font-semibold text-ink leading-tight">{m.name}</p>
              <p className="mt-0.5 text-[13px] text-ink-2">
                {t("order.planned")} <span className={overdue ? "font-medium text-red" : ""}>{fmtDate(m.plannedDate, lang)}</span>
                {done && <> · <span className="text-green-text font-medium">{t("order.actual")} {fmtDate(m.actualDate, lang)}</span></>}
              </p>
            </div>
            {m.manual && onTick && (
              <Button variant="secondary" className="min-h-[36px] px-3 text-[13px] rounded-md shadow-xs" loading={busyId === m.id} onClick={() => onTick(m)}>
                {done ? t("order.untick") : t("order.tick")}
              </Button>
            )}
          </li>
        );
      })}
    </ol>
  );
}

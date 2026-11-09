import { useT } from "../../../i18n/provider";
import type { Health } from "../../../api/types";
import { StatusGlyph } from "../../../components/ui";

const ORDER: Health[] = ["RED", "AMBER", "GREEN", "GREY"];
const KEY: Record<Health, string> = { RED: "status.red", AMBER: "status.amber", GREEN: "status.green", GREY: "status.grey" };

/** Four plain counts with their shape glyph. Clicking one filters the table: no cards, no charts. */
export function SummaryStrip({ counts, active, onPick }: { counts: Record<Health, number>; active?: Health; onPick: (h: Health | undefined) => void }) {
  const t = useT();
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1" role="group" aria-label={t("merch.status")}>
      {ORDER.map((h) => (
        <button key={h} type="button" aria-pressed={active === h} onClick={() => onPick(active === h ? undefined : h)}
                className={`press inline-flex min-h-[44px] items-center gap-2 border-b-2 text-[14px] transition-colors duration-150 ${active === h ? "border-ink font-semibold text-ink" : "border-transparent text-ink-2 hover:border-line-strong hover:text-ink"}`}>
          <StatusGlyph health={h} /> <span className="font-semibold text-ink">{counts[h]}</span> {t(KEY[h])}
        </button>
      ))}
    </div>
  );
}

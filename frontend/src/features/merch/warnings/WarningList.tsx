import { useT } from "../../../i18n/provider";
import type { WarningView } from "../../../api/types";
import { StatusGlyph } from "../../../components/ui";
import { stageKey } from "../board/shared";

export function WarningList({ items, selected, onSelect }: { items: WarningView[]; selected: string | null; onSelect: (id: string) => void }) {
  const t = useT();
  return (
    <ul className="flex flex-col divide-y divide-line rounded-lg border border-line bg-surface shadow-xs overflow-hidden">
      {items.map((w) => {
        const cat = w.note ? (w.note.category as string) : "NEEDS_REVIEW";
        return (
          <li key={w.id}>
            <button type="button" onClick={() => onSelect(w.id)} aria-current={selected === w.id || undefined}
                    className={`flex min-h-[64px] w-full items-start gap-3 px-4 py-3.5 text-left transition-colors duration-150 ${
                      selected === w.id ? "bg-[#F5F3EC]" : "hover:bg-[#FAF8F4]"
                    }`}>
              <StatusGlyph health={w.health} className="mt-1" />
              <span className="min-w-0">
                <span className="block font-semibold text-ink">{w.poNo}</span>
                <span className="block truncate text-[13px] text-ink-2">{t(`cat.${cat}`)} · {t(stageKey(w.snapshot.activeStage))}</span>
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}

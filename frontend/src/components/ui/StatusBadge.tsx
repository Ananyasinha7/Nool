import { useT } from "../../i18n/provider";
import type { Health } from "../../api/types";

// Status is never colour alone: shape + word + tint (Doc2 section 2.5, NFR-4).
const META: Record<Health, { glyph: string; key: string; cls: string; dotCls: string }> = {
  GREEN: { glyph: "●", key: "status.green", cls: "bg-green-bg text-green-text border border-[#CDE3D5]", dotCls: "text-green" },
  AMBER: { glyph: "▲", key: "status.amber", cls: "bg-amber-bg text-amber-text border border-[#F5E4C2]", dotCls: "text-amber" },
  RED: { glyph: "■", key: "status.red", cls: "bg-red-bg text-red-text border border-[#F3D7CF]", dotCls: "text-red" },
  GREY: { glyph: "○", key: "status.grey", cls: "bg-paper text-ink-2 border border-line", dotCls: "text-ink-3" },
};

export function StatusGlyph({ health, className = "" }: { health: Health; className?: string }) {
  const color = { GREEN: "text-green", AMBER: "text-amber", RED: "text-red", GREY: "text-grey" }[health];
  return <span aria-hidden="true" className={`${color} ${className}`}>{META[health].glyph}</span>;
}

export function StatusBadge({ health }: { health: Health }) {
  const t = useT();
  const m = META[health];
  return (
    <span className={`inline-flex max-w-full items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-0.5 text-[12px] font-medium tracking-[0.01em] ${m.cls}`}>
      <span aria-hidden="true" className={`text-[10px] leading-none ${m.dotCls}`}>{m.glyph}</span>
      <span className="truncate">{t(m.key)}</span>
    </span>
  );
}

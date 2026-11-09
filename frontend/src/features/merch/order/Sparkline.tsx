import { useI18n } from "../../../i18n/provider";
import { fmtDate } from "../../../lib/format";

/** The only chart in the product: 10 bars, one colour, no axes, first and last date only (Doc2 S-3). */
export function Sparkline({ points }: { points: { date: string; qty: number }[] }) {
  const { lang } = useI18n();
  if (points.length === 0) return null;
  const max = Math.max(1, ...points.map((p) => p.qty));
  const w = 12, gap = 6, h = 48;
  const width = points.length * (w + gap) - gap;
  return (
    <figure className="flex flex-col gap-1">
      <svg role="img" aria-label={points.map((p) => `${p.date}: ${p.qty}`).join(", ")} width="100%" viewBox={`0 0 ${width} ${h}`} preserveAspectRatio="none" className="h-12 max-w-xs">
        {points.map((p, i) => {
          const bh = Math.max(1, (p.qty / max) * h);
          return <rect key={p.date} x={i * (w + gap)} y={h - bh} width={w} height={bh} fill="var(--ink)" />;
        })}
      </svg>
      <figcaption className="flex max-w-xs justify-between text-[12px] text-ink-3">
        <span>{fmtDate(points[0].date, lang)}</span><span>{fmtDate(points[points.length - 1].date, lang)}</span>
      </figcaption>
    </figure>
  );
}

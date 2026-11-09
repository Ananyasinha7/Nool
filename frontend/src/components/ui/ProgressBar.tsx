import type { Health } from "../../api/types";

const FILL: Record<Health, string> = { GREEN: "bg-green", AMBER: "bg-amber", RED: "bg-red", GREY: "bg-grey" };

interface Props {
  done: number;
  qty: number;
  health?: Health;
  /** pieces that will exist at the deadline at the current rate (Doc3 section 17), drawn as a hairline tick */
  tickAt?: number;
  label?: string;
  /** buyers see progress only, never a status colour (BR-05) */
  neutral?: boolean;
}

export function ProgressBar({ done, qty, health = "GREEN", tickAt, label, neutral }: Props) {
  const p = qty > 0 ? Math.min(100, (100 * done) / qty) : 0;
  const tick = tickAt !== undefined && qty > 0 ? Math.min(100, (100 * tickAt) / qty) : null;
  return (
    <div role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(p)} aria-label={label}
         className="relative h-2 w-full overflow-hidden rounded-full bg-[#EAE7DF]">
      <div className={`h-full rounded-full transition-all duration-300 ease-out ${neutral ? "bg-ink" : FILL[health]}`} style={{ width: `${p}%` }} />
      {tick !== null && (
        <div
          aria-hidden="true"
          title="Deadline target"
          className="absolute -top-0.5 bottom-0 h-3 w-[1.5px] -translate-x-1/2 bg-ink shadow-sm"
          style={{ left: `${tick}%` }}
        />
      )}
    </div>
  );
}

import { useEffect, useRef } from "react";
import { useT } from "../../i18n/provider";

interface Props { value: string; onChange: (v: string) => void; hint?: number | null; error?: string | null }
const digits = (s: string) => s.replace(/\D/g, "").slice(0, 7);

/** Large number, -/+ buttons, +10 +50 +100 chips; tap the number to type (Doc2 C-04). Hold +/- to repeat. */
export function QuantityStepper({ value, onChange, hint, error }: Props) {
  const t = useT();
  const cur = useRef(value);
  cur.current = value;
  const hold = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  const set = (n: number) => onChange(String(Math.max(0, n)));
  const bump = (d: number) => set((Number(cur.current) || 0) + d);
  const startHold = (d: number) => { bump(d); const t0 = setTimeout(() => { hold.current = setInterval(() => bump(d * 5), 120); }, 400); hold.current = t0 as unknown as ReturnType<typeof setInterval>; };
  const stopHold = () => { clearInterval(hold.current); clearTimeout(hold.current as unknown as ReturnType<typeof setTimeout>); };
  useEffect(() => stopHold, []);
  const btn = "press flex min-h-[56px] min-w-[56px] items-center justify-center rounded border border-field bg-surface text-[28px]";
  return (
    <div className="flex flex-col items-center gap-3">
      <label htmlFor="qty" className="text-label text-ink-2">{t("sup.todayCount")}</label>
      <div className="flex w-full items-center justify-between gap-2">
        <button type="button" aria-label="−" className={btn} onPointerDown={() => startHold(-1)} onPointerUp={stopHold} onPointerLeave={stopHold}>−</button>
        <input id="qty" inputMode="numeric" pattern="[0-9]*" autoComplete="off" value={value} placeholder={hint ? String(hint) : "0"}
               aria-invalid={!!error || undefined} aria-describedby={error ? "qty-err" : undefined}
               onChange={(e) => onChange(digits(e.target.value))}
               className="min-w-0 flex-1 bg-transparent text-center text-display placeholder:text-ink-3" />
        <button type="button" aria-label="+" className={btn} onPointerDown={() => startHold(1)} onPointerUp={stopHold} onPointerLeave={stopHold}>+</button>
      </div>
      <div className="flex gap-2">
        {[10, 50, 100].map((n) => <button key={n} type="button" onClick={() => bump(n)} className="press min-h-[48px] min-w-[72px] rounded-full border border-field bg-surface px-4 font-medium">+{n}</button>)}
      </div>
      {error && <p id="qty-err" role="alert" aria-live="polite" className="text-red">⚠ {error}</p>}
    </div>
  );
}

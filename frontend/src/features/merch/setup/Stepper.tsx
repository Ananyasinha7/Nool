import { useT } from "../../../i18n/provider";

export function Stepper({ step, onGo, maxReached }: { step: number; onGo: (n: number) => void; maxReached: number }) {
  const t = useT();
  return (
    <ol className="flex gap-2 overflow-x-auto" aria-label={t("setup.title")}>
      {[1, 2, 3, 4].map((n) => (
        <li key={n} className="flex-1">
          <button type="button" disabled={n > maxReached} onClick={() => onGo(n)} aria-current={step === n ? "step" : undefined}
                  className={`flex min-h-[44px] w-full flex-col items-start border-t-2 pt-2 text-left text-[13px] ${step === n ? "border-ink font-semibold" : n <= maxReached ? "border-field text-ink-2" : "border-line text-ink-3"}`}>
            <span className="text-ink-3">{n}</span>{t(`setup.step${n}`)}
          </button>
        </li>
      ))}
    </ol>
  );
}

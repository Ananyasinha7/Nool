import { useI18n } from "../../i18n/provider";
import { fmtDateYear } from "../../lib/format";
import { isDemoClock, useToday } from "../../lib/today";

/** Explains to reviewers why the seeded colours stay stable (A-13, Doc2 C-19). */
export function DemoClockChip() {
  const { t, lang } = useI18n();
  const today = useToday();
  if (!isDemoClock(today)) return null;
  return <span className="whitespace-nowrap rounded-full border border-field px-2.5 py-0.5 text-label text-ink-2">{t("common.demoDate")} {fmtDateYear(today, lang)}</span>;
}

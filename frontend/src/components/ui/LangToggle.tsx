import { useI18n } from "../../i18n/provider";

export function LangToggle() {
  const { lang, setLang, t } = useI18n();
  const opt = (l: "en" | "ta", label: string) => (
    <button type="button" aria-pressed={lang === l} lang={l} onClick={() => setLang(l)}
            className={`min-h-[32px] px-3 text-label ${lang === l ? "bg-ink text-paper" : "bg-surface text-ink-2"}`}>{label}</button>
  );
  return (
    <div role="group" aria-label={t("common.language")} className="inline-flex overflow-hidden rounded border border-field">
      {opt("en", "EN")}{opt("ta", "தமிழ்")}
    </div>
  );
}

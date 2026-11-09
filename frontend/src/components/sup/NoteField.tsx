import { useT } from "../../i18n/provider";

export function NoteField({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const t = useT();
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor="note" className="text-label text-ink-2">{t("sup.note")}</label>
      <textarea id="note" rows={3} maxLength={500} value={value} onChange={(e) => onChange(e.target.value)} lang="ta"
                className="w-full rounded border border-field bg-surface p-3 text-[16px]" />
    </div>
  );
}

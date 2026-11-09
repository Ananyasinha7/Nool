import { useI18n } from "../../../i18n/provider";
import type { EditableCategory, NoteView } from "../../../api/types";
import { Select } from "../../../components/ui";

export const CATEGORIES: EditableCategory[] = ["MACHINE_BREAKDOWN", "POWER_CUT", "ABSENTEEISM", "MATERIAL_SHORTAGE", "QUALITY_REWORK", "SUBCONTRACTOR_DELAY", "APPROVAL_PENDING", "OTHER"];

interface Props { note: NoteView; value: EditableCategory | ""; onCategory: (c: EditableCategory) => void; highlight?: boolean; disabled?: boolean }

/** Original note on the left, English translation and category on the right; stacked on mobile (Doc2 C-11). */
export function NoteCompare({ note, value, onCategory, highlight, disabled }: Props) {
  const { t } = useI18n();
  const source = note.source === "AI" ? t("warn.aiSource") : note.source === "RULE" ? t("warn.ruleSource") : t("warn.humanSource");
  const conf = note.confidence === null ? null : note.confidence >= 0.85 ? t("warn.confHigh") : t("warn.confUnsure");
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div>
        <p className="mb-1 text-label text-ink-3">{t("order.original")}</p>
        <p lang={note.lang} className="rounded border border-line bg-paper p-3 text-[16px]">{note.originalText}</p>
      </div>
      <div className="flex flex-col gap-3">
        <div>
          <p className="mb-1 text-label text-ink-3">{t("order.translation")}</p>
          <p className="rounded border border-line bg-surface p-3">{note.translationEn || "—"}</p>
        </div>
        <div className={highlight ? "rounded outline outline-2 outline-ink outline-offset-4" : ""}>
          <Select label={t("order.category")} value={value} placeholder={t("cat.NEEDS_REVIEW")} disabled={disabled}
                  options={CATEGORIES.map((c) => ({ value: c, label: t(`cat.${c}`) }))} onChange={(v) => v && onCategory(v as EditableCategory)} />
        </div>
        <p className="text-[13px] text-ink-3">{source}{conf ? ` · ${conf}` : ""}{note.needsReview ? ` · ${t("warn.needsReview")}` : ""}</p>
      </div>
    </div>
  );
}

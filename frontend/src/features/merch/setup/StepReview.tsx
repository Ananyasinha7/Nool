import { useI18n } from "../../../i18n/provider";
import { fmtDateYear, fmtNum } from "../../../lib/format";
import type { Lookups, TnaTemplateOut } from "../../../api/types";
import { Button } from "../../../components/ui";
import { planDates, totalQty, type SetupState } from "./validation";

interface Props { s: SetupState; lookups?: Lookups; templates: TnaTemplateOut[]; onEdit: (step: number) => void }

export function StepReview({ s, lookups, templates, onEdit }: Props) {
  const { t, lang } = useI18n();
  const buyer = lookups?.buyers.find((b) => b.id === s.buyerId)?.name ?? "";
  const unit = lookups?.units.find((u) => u.id === s.unitId)?.name ?? "";
  const plan = planDates(templates.find((x) => x.id === s.templateId), s);
  const row = (label: string, value: string, step: number) => (
    <div className="flex items-start justify-between gap-4 border-b border-line py-2 last:border-b-0">
      <div><p className="text-label text-ink-3">{label}</p><p>{value}</p></div>
      <Button variant="ghost" className="min-h-[36px] px-2" onClick={() => onEdit(step)}>{t("setup.edit")}</Button>
    </div>
  );
  return (
    <div className="rounded-md border border-line bg-surface px-4">
      {row(t("setup.po"), `${s.poNo} · ${buyer}`, 1)}
      {row(t("setup.style"), `${s.style}, ${s.colour} · ${unit}`, 1)}
      {row(t("setup.total"), `${fmtNum(totalQty(s.lines))} ${t("common.pcs")}`, 2)}
      {row(t("setup.exFactory"), fmtDateYear(s.exFactory, lang), 3)}
      {row(t("setup.milestones"), plan.map((m) => m.name).join(" · "), 3)}
    </div>
  );
}

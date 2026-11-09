import { useI18n } from "../../../i18n/provider";
import { fmtDate } from "../../../lib/format";
import type { TnaTemplateOut } from "../../../api/types";
import { FormField, Select, inputCls } from "../../../components/ui";
import { planDates, type Errors, type SetupState } from "./validation";

interface Props { s: SetupState; set: (p: Partial<SetupState>) => void; errors: Errors; templates: TnaTemplateOut[] }

export function StepPlan({ s, set, errors, templates }: Props) {
  const { t, lang } = useI18n();
  const tpl = templates.find((x) => x.id === s.templateId);
  const plan = planDates(tpl, s);
  return (
    <div className="flex flex-col gap-5">
      <div className="grid gap-4 md:grid-cols-2">
        <FormField label={t("setup.exFactory")} error={errors.exFactory ? t(errors.exFactory) : null}>
          {({ id, describedBy, invalid }) => <input id={id} type="date" aria-describedby={describedBy} className={inputCls(invalid)} value={s.exFactory} onChange={(e) => set({ exFactory: e.target.value, overrides: {} })} />}
        </FormField>
        <Select label={t("setup.template")} value={s.templateId} placeholder="—" error={errors.templateId ? t(errors.templateId) : null}
                options={templates.map((x) => ({ value: x.id, label: x.name }))} onChange={(v) => set({ templateId: v })} />
      </div>
      {plan.length > 0 && (
        <div>
          <h3 className="mb-2 text-heading">{t("setup.milestones")}</h3>
          <ul className="flex flex-col divide-y divide-line rounded-md border border-line bg-surface">
            {plan.map((m) => (
              <li key={m.name} className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
                <span>{m.name}</span>
                <span className="flex items-center gap-3">
                  <span className="text-ink-2">{fmtDate(m.date, lang)}</span>
                  <input aria-label={m.name} type="date" className="min-h-[36px] rounded border border-field px-2" value={m.date}
                         onChange={(e) => set({ overrides: { ...s.overrides, [m.name]: e.target.value } })} />
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

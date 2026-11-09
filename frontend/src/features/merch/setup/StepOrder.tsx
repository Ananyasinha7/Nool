import { useT } from "../../../i18n/provider";
import type { Lookups } from "../../../api/types";
import { Select, TextInput } from "../../../components/ui";
import type { Errors, SetupState } from "./validation";

interface Props { s: SetupState; set: (p: Partial<SetupState>) => void; errors: Errors; lookups?: Lookups; poError?: string }

export function StepOrder({ s, set, errors, lookups, poError }: Props) {
  const t = useT();
  const err = (k: string) => (errors[k] ? t(errors[k]) : null);
  const units = (lookups?.units ?? []).map((u) => ({ value: u.id, label: u.name }));
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <TextInput label={t("setup.po")} value={s.poNo} onChange={(e) => set({ poNo: e.target.value })} error={poError ?? err("poNo")} />
      <Select label={t("merch.buyer")} value={s.buyerId} placeholder={t("setup.pickBuyer")} error={err("buyerId")} onChange={(v) => set({ buyerId: v })}
              options={(lookups?.buyers ?? []).map((b) => ({ value: b.id, label: b.name }))} />
      <TextInput label={t("setup.style")} value={s.style} onChange={(e) => set({ style: e.target.value })} error={err("style")} />
      <TextInput label={t("setup.colour")} value={s.colour} onChange={(e) => set({ colour: e.target.value })} error={err("colour")} />
      <Select label={t("merch.unit")} value={s.unitId} placeholder={t("setup.pickUnit")} error={err("unitId")} onChange={(v) => set({ unitId: v })} options={units} />
      <div className="flex flex-col gap-3">
        <label className="flex min-h-[44px] items-center gap-3">
          <input type="checkbox" className="h-5 w-5" checked={s.hasPrint} onChange={(e) => set({ hasPrint: e.target.checked })} />
          {t("setup.hasPrint")}
        </label>
        {s.hasPrint && <Select label={t("setup.printUnit")} value={s.printUnitId} placeholder={t("setup.pickUnit")} options={units} onChange={(v) => set({ printUnitId: v })} />}
      </div>
    </div>
  );
}

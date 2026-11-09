import { useT } from "../../../i18n/provider";
import { fmtNum } from "../../../lib/format";
import { Button, FormField, inputCls } from "../../../components/ui";
import { totalQty, type Errors, type SetupState } from "./validation";

export function StepQuantities({ s, set, errors }: { s: SetupState; set: (p: Partial<SetupState>) => void; errors: Errors }) {
  const t = useT();
  const upd = (i: number, patch: Partial<{ size: string; qty: string }>) => set({ lines: s.lines.map((l, j) => (j === i ? { ...l, ...patch } : l)) });
  const total = totalQty(s.lines);
  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
        {s.lines.map((l, i) => (
          <FormField key={i} label={l.size || t("setup.size")} error={null}>
            {({ id }) => <input id={id} inputMode="numeric" className={inputCls(false)} value={l.qty} onChange={(e) => upd(i, { qty: e.target.value })} />}
          </FormField>
        ))}
      </div>
      {errors.lines && <p role="alert" className="text-[13px] text-red">⚠ {t(errors.lines)}</p>}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button variant="ghost" onClick={() => set({ lines: [...s.lines, { size: `${s.lines.length + 1}`, qty: "" }] })}>+ {t("setup.addSize")}</Button>
        <p className="text-heading">{t("setup.total")}: {fmtNum(total)}</p>
      </div>
    </div>
  );
}

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiException, errorKey } from "../../../api/client";
import { useI18n } from "../../../i18n/provider";
import { useAsync } from "../../../lib/useAsync";
import { useToday } from "../../../lib/today";
import { usePageTitle } from "../../../lib/usePageTitle";
import { Button, ErrorState, Skeleton, useToast } from "../../../components/ui";
import { Stepper } from "./Stepper";
import { StepOrder } from "./StepOrder";
import { StepPlan } from "./StepPlan";
import { StepQuantities } from "./StepQuantities";
import { StepReview } from "./StepReview";
import { emptyState, planDates, step1Errors, step2Errors, step3Errors, toPayload, type Errors, type SetupState } from "./validation";

const SHOW_SAMPLE = import.meta.env.DEV || import.meta.env.VITE_DEMO_LOGINS === "true";

export default function SetupPage() {
  const { t } = useI18n();
  usePageTitle(t("setup.title"));
  const toast = useToast();
  const nav = useNavigate();
  const today = useToday();
  const lookups = useAsync(() => api.lookups(), []);
  const templates = useAsync(() => api.templates(), []);
  const [s, setS] = useState<SetupState>(emptyState);
  const [step, setStep] = useState(1);
  const [reached, setReached] = useState(1);
  const [showErrors, setShowErrors] = useState(false);
  const [poError, setPoError] = useState<string | undefined>();
  const [busy, setBusy] = useState(false);
  const set = (p: Partial<SetupState>) => { setS((x) => ({ ...x, ...p })); if ("poNo" in p) setPoError(undefined); };

  const errors: Errors = useMemo(() => (step === 1 ? step1Errors(s) : step === 2 ? step2Errors(s) : step === 3 ? step3Errors(s, today) : {}), [s, step, today]);
  const valid = Object.keys(errors).length === 0;

  function go(n: number) { setStep(n); setReached((r) => Math.max(r, n)); setShowErrors(false); }
  async function create() {
    setBusy(true);
    try {
      const { id } = await api.createOrder(toPayload(s, planDates(templates.data?.find((x) => x.id === s.templateId), s)));
      toast.show(t("setup.created"));
      nav(`/orders/${id}`);
    } catch (e) {
      if (e instanceof ApiException && e.fields?.poNo) { setPoError(t("setup.dupPo")); setStep(1); }
      else toast.show(t(errorKey(e)));
    } finally { setBusy(false); }
  }
  function loadSample() {
    const b = lookups.data?.buyers.find((x) => x.name === "Company B")?.id ?? "";
    const u = lookups.data?.units.find((x) => x.name === "Unit 1")?.id ?? "";
    const q = [1200, 3000, 3600, 3000, 1200];
    setS({ ...emptyState(), poNo: "B-PO-88213", buyerId: b, style: "Men's crew neck tee", colour: "navy", unitId: u,
      lines: ["S", "M", "L", "XL", "XXL"].map((size, i) => ({ size, qty: String(q[i]) })), exFactory: "2026-11-20", templateId: templates.data?.[0]?.id ?? "" });
    setReached(4);
  }

  if (lookups.error || templates.error) return <ErrorState message={t(errorKey(lookups.error ?? templates.error))} onRetry={() => { lookups.reload(); templates.reload(); }} />;
  if (!lookups.data || !templates.data) return <Skeleton className="h-64 w-full" />;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-title">{t("setup.title")}</h1>
        {SHOW_SAMPLE && <Button variant="ghost" onClick={loadSample}>{t("setup.loadSample")}</Button>}
      </div>
      <Stepper step={step} onGo={go} maxReached={reached} />
      <section aria-label={t(`setup.step${step}`)}>
        {step === 1 && <StepOrder s={s} set={set} errors={showErrors ? errors : {}} lookups={lookups.data} poError={poError} />}
        {step === 2 && <StepQuantities s={s} set={set} errors={showErrors ? errors : {}} />}
        {step === 3 && <StepPlan s={s} set={set} errors={showErrors ? errors : {}} templates={templates.data} />}
        {step === 4 && <StepReview s={s} lookups={lookups.data} templates={templates.data} onEdit={go} />}
      </section>
      <div className="flex justify-between gap-3">
        <Button variant="ghost" disabled={step === 1} onClick={() => go(step - 1)}>{t("common.back")}</Button>
        {step < 4
          ? <Button onClick={() => (valid ? go(step + 1) : setShowErrors(true))}>{t("common.next")}</Button>
          : <Button loading={busy} onClick={create}>{t("setup.create")}</Button>}
      </div>
    </div>
  );
}

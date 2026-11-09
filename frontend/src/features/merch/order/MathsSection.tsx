import { useI18n } from "../../../i18n/provider";
import { fmtNum } from "../../../lib/format";
import type { OrderHealth } from "../../../api/types";
import { MathsPanel, ProgressBar } from "../../../components/ui";
import { stageKey } from "../board/shared";

/** The first thing under the header: the product's signature element (Doc2 S-3). */
export function MathsSection({ h }: { h: OrderHealth }) {
  const { t } = useI18n();
  return (
    <section className="flex flex-col gap-3.5 rounded-lg border border-line bg-surface p-5 shadow-xs" aria-label="Projection">
      <div className="flex items-baseline justify-between gap-4">
        <p className="text-heading">{t(stageKey(h.activeStage))}</p>
        <p className="text-heading">{fmtNum(h.done)} <span className="text-ink-3">/ {fmtNum(h.qty)}</span></p>
      </div>
      <ProgressBar done={h.done} qty={h.qty} health={h.health} tickAt={h.projectedAtDeadline} label={t(stageKey(h.activeStage))} />
      <MathsPanel h={h} />
    </section>
  );
}

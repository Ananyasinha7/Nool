import { useT } from "../../../i18n/provider";

/** Exactly what the buyer will see (Doc2 S-5). */
export function BuyerPreview({ text }: { text: string }) {
  const t = useT();
  return (
    <div>
      <p className="mb-1.5 text-label font-medium uppercase tracking-wider text-ink-3">{t("warn.buyerPreview")}</p>
      <p lang="en" className="rounded-lg border border-[#F5E4C2] bg-amber-bg p-3.5 text-amber-text font-medium shadow-xs">
        <span aria-hidden="true" className="mr-1 text-amber">▲</span>{text}
      </p>
    </div>
  );
}

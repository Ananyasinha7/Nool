import type { BuyerOrderView } from "../../api/types";

/** Only a CONFIRMED notice ever reaches here; the text is the category label plus date impact (D-17). */
export function DelayNotice({ n }: { n: NonNullable<BuyerOrderView["delayNotice"]> }) {
  return <p role="note" lang="en" className="rounded border border-amber bg-amber-bg px-3 py-2 text-amber-text"><span aria-hidden="true">▲ </span>{n.text}</p>;
}

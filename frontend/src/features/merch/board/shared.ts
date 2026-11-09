import type { OrderSummary } from "../../../api/types";

export const stageKey = (s: string | null): string => (s ? `stage.${s.toLowerCase()}` : "stage.done");

/** The sentence under the status: how the projection was reached (Doc2 principle 5). */
export function projectionKeys(o: OrderSummary) {
  const h = o.health;
  const flagKey = h.health === "GREEN" || h.health === "GREY" ? null
    : h.leadDays >= 14 ? "merch.flaggedEarly" : "merch.flaggedBefore";
  return { flagKey, flagN: h.leadDays };
}

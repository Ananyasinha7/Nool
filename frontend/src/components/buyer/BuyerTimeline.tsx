import type { BuyerOrderDetail } from "../../api/types";
import { Timeline } from "../ui";

// "0000-00-00" as today means nothing is ever flagged overdue: no status colour for buyers (BR-05).
export function BuyerTimeline({ items }: { items: BuyerOrderDetail["milestones"] }) {
  return <Timeline today="0000-00-00" items={items.map((m) => ({ name: m.name, plannedDate: m.plannedDate, actualDate: m.actualDate }))} />;
}

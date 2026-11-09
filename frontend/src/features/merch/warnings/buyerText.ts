// Mirrors backend/app/services/warnings.py buyer_text(): the buyer sees a category label plus date impact,
// never the raw floor note (D-17). Buyer text is English only. The test pins the exact server strings.
const LABEL: Record<string, string> = {
  MACHINE_BREAKDOWN: "Machine breakdown", POWER_CUT: "Power cut", ABSENTEEISM: "Staff absence",
  MATERIAL_SHORTAGE: "Material shortage", QUALITY_REWORK: "Quality rework", SUBCONTRACTOR_DELAY: "Subcontractor delay",
  APPROVAL_PENDING: "Approval pending", OTHER: "Production issue", NEEDS_REVIEW: "Production issue",
};

export function buyerText(category: string, shipSlipDays: number): string {
  const label = LABEL[category] ?? "Production issue";
  if (shipSlipDays > 0) return `Delay notice · ${label} · ship date may move by about ${shipSlipDays} ${shipSlipDays === 1 ? "day" : "days"}`;
  return `Delay notice · ${label} · we are monitoring the ship date`;
}

import type { OrderCreate, TnaTemplateOut } from "../../../api/types";

export interface SizeLine { size: string; qty: string }
export interface SetupState {
  poNo: string; buyerId: string; style: string; colour: string; unitId: string;
  hasPrint: boolean; printUnitId: string;
  lines: SizeLine[];
  exFactory: string; templateId: string;
  overrides: Record<string, string>;   // milestone name -> edited date
}
export type Errors = Record<string, string>; // field -> i18n key

export const DEFAULT_SIZES = ["S", "M", "L", "XL", "XXL"];
export const emptyState = (): SetupState => ({
  poNo: "", buyerId: "", style: "", colour: "", unitId: "", hasPrint: false, printUnitId: "",
  lines: DEFAULT_SIZES.map((size) => ({ size, qty: "" })), exFactory: "", templateId: "", overrides: {},
});

const wholePositive = (v: string) => /^\d+$/.test(v.trim()) && Number(v) > 0;

export function totalQty(lines: SizeLine[]): number {
  return lines.reduce((n, l) => n + (wholePositive(l.qty) ? Number(l.qty) : 0), 0);
}

export function step1Errors(s: SetupState): Errors {
  const e: Errors = {};
  if (!s.poNo.trim()) e.poNo = "setup.required";
  if (!s.buyerId) e.buyerId = "setup.required";
  if (!s.style.trim()) e.style = "setup.required";
  if (!s.colour.trim()) e.colour = "setup.required";
  if (!s.unitId) e.unitId = "setup.required";
  return e;
}

export function step2Errors(s: SetupState): Errors {
  const e: Errors = {};
  const filled = s.lines.filter((l) => l.qty.trim() !== "");
  if (filled.length === 0) e.lines = "setup.noLines";
  else if (filled.some((l) => !wholePositive(l.qty))) e.lines = "setup.qtyInvalid";
  const sizes = s.lines.map((l) => l.size.trim().toLowerCase()).filter(Boolean);
  if (new Set(sizes).size !== sizes.length) e.lines = "setup.qtyInvalid";
  return e;
}

export function step3Errors(s: SetupState, today: string): Errors {
  const e: Errors = {};
  if (!s.exFactory) e.exFactory = "setup.required";
  else if (s.exFactory <= today) e.exFactory = "setup.dateFuture";
  if (!s.templateId) e.templateId = "setup.required";
  return e;
}

export function subDays(iso: string, n: number): string {
  const d = new Date(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10)));
  d.setUTCDate(d.getUTCDate() - n);
  return d.toISOString().slice(0, 10);
}

export interface PlannedMilestone { name: string; kind: "STAGE" | "MANUAL"; date: string; edited: boolean }

/** Same rule as the server (F-3): ex-factory minus offsetDays; print-only items skipped without print.
 * The server re-derives and validates; this is the preview the merchandiser can edit (FR-04). */
export function planDates(tpl: TnaTemplateOut | undefined, s: SetupState): PlannedMilestone[] {
  if (!tpl || !s.exFactory) return [];
  return tpl.items
    .filter((i) => !i.printOnly || s.hasPrint)
    .sort((a, b) => b.offsetDays - a.offsetDays)
    .map((i) => {
      const edited = s.overrides[i.name] !== undefined;
      return { name: i.name, kind: i.kind, date: s.overrides[i.name] ?? subDays(s.exFactory, i.offsetDays), edited };
    });
}

export function toPayload(s: SetupState, plan: PlannedMilestone[]): OrderCreate {
  const milestoneDates: Record<string, string> = {};
  for (const m of plan) if (m.edited) milestoneDates[m.name] = m.date; // only send what the person changed
  return {
    poNo: s.poNo.trim(), buyerId: s.buyerId, style: s.style.trim(), colour: s.colour.trim(), unitId: s.unitId,
    printUnitId: s.hasPrint && s.printUnitId ? s.printUnitId : null, washUnitId: null,
    hasPrint: s.hasPrint, hasWash: false, exFactory: s.exFactory, templateId: s.templateId,
    lines: s.lines.filter((l) => wholePositive(l.qty)).map((l) => ({ size: l.size.trim(), qty: Number(l.qty) })),
    milestoneDates: Object.keys(milestoneDates).length ? milestoneDates : null,
  };
}

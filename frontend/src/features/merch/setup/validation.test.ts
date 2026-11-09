import { describe, expect, it } from "vitest";
import type { TnaTemplateOut } from "../../../api/types";
import { emptyState, planDates, step1Errors, step2Errors, step3Errors, subDays, toPayload, totalQty } from "./validation";

const tpl: TnaTemplateOut = {
  id: "t", name: "Standard",
  items: [
    { name: "Sample approved", kind: "MANUAL", stageKey: null, offsetDays: 40, printOnly: false },
    { name: "Printing complete", kind: "STAGE", stageKey: "PRINTING", offsetDays: 16, printOnly: true },
    { name: "Stitching complete", kind: "STAGE", stageKey: "STITCHING", offsetDays: 7, printOnly: false },
  ],
};

describe("order setup validation", () => {
  it("step 1 requires every field", () => {
    expect(Object.keys(step1Errors(emptyState())).sort()).toEqual(["buyerId", "colour", "poNo", "style", "unitId"]);
  });
  it("total is the sum of valid lines only", () => {
    const s = emptyState();
    s.lines[0].qty = "600"; s.lines[1].qty = "400"; s.lines[2].qty = "abc";
    expect(totalQty(s.lines)).toBe(1000);
  });
  it("step 2 needs a quantity and rejects decimals, negatives and duplicate sizes", () => {
    const s = emptyState();
    expect(step2Errors(s).lines).toBe("setup.noLines");
    s.lines[0].qty = "1.5";
    expect(step2Errors(s).lines).toBe("setup.qtyInvalid");
    s.lines[0].qty = "-3";
    expect(step2Errors(s).lines).toBe("setup.qtyInvalid");
    s.lines[0].qty = "10"; s.lines[1].size = "S"; s.lines[1].qty = "5";
    expect(step2Errors(s).lines).toBe("setup.qtyInvalid");
  });
  it("step 3 needs a future date", () => {
    const s = emptyState(); s.templateId = "t";
    expect(step3Errors(s, "2026-11-03").exFactory).toBe("setup.required");
    s.exFactory = "2026-11-03";
    expect(step3Errors(s, "2026-11-03").exFactory).toBe("setup.dateFuture");
    s.exFactory = "2026-12-30";
    expect(step3Errors(s, "2026-11-03")).toEqual({});
  });
  it("date maths crosses month and year ends", () => {
    expect(subDays("2026-12-30", 7)).toBe("2026-12-23");
    expect(subDays("2027-01-05", 10)).toBe("2026-12-26");
  });
  it("plan dates count back from ex-factory and skip print-only without print", () => {
    const s = emptyState(); s.exFactory = "2026-12-30";
    expect(planDates(tpl, s).map((m) => m.name)).toEqual(["Sample approved", "Stitching complete"]);
    expect(planDates(tpl, s)[1].date).toBe("2026-12-23");
    s.hasPrint = true;
    expect(planDates(tpl, s).map((m) => m.name)).toContain("Printing complete");
  });
  it("only edited milestone dates go to the server", () => {
    const s = emptyState();
    Object.assign(s, { poNo: " P1 ", buyerId: "b", style: "x", colour: "y", unitId: "u", exFactory: "2026-12-30", templateId: "t" });
    s.lines[0].qty = "100";
    s.overrides["Stitching complete"] = "2026-12-20";
    const p = toPayload(s, planDates(tpl, s));
    expect(p.poNo).toBe("P1");
    expect(p.milestoneDates).toEqual({ "Stitching complete": "2026-12-20" });
    expect(p.lines).toEqual([{ size: "S", qty: 100 }]);
  });
});

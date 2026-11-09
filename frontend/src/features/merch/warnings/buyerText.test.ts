import { describe, expect, it } from "vitest";
import { buyerText } from "./buyerText";

describe("buyerText matches the server", () => {
  it("with a ship slip", () => {
    expect(buyerText("MACHINE_BREAKDOWN", 3)).toBe("Delay notice · Machine breakdown · ship date may move by about 3 days");
  });
  it("singular day", () => {
    expect(buyerText("POWER_CUT", 1)).toBe("Delay notice · Power cut · ship date may move by about 1 day");
  });
  it("no slip yet", () => {
    expect(buyerText("MATERIAL_SHORTAGE", 0)).toBe("Delay notice · Material shortage · we are monitoring the ship date");
  });
  it("unknown and review categories are generic", () => {
    expect(buyerText("NEEDS_REVIEW", 2)).toContain("Production issue");
    expect(buyerText("???", 0)).toContain("Production issue");
  });
});

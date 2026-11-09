import { describe, expect, it } from "vitest";
import { activeCount, apiQuery, parseFilters, toParams } from "./filters";

describe("board filters", () => {
  it("round-trips through the URL", () => {
    const f = { buyerId: "b1", unitId: "u1", week: "2026-W47", status: "RED" as const, q: "88" };
    expect(parseFilters(toParams(f))).toEqual(f);
  });
  it("ignores unknown statuses and empty values", () => {
    const f = parseFilters(new URLSearchParams("status=PURPLE&buyer="));
    expect(f.status).toBeUndefined();
    expect(f.buyerId).toBeUndefined();
  });
  it("filters combine and are counted", () => {
    expect(activeCount({ buyerId: "b", status: "RED" })).toBe(2);
    expect(activeCount({})).toBe(0);
  });
  it("status is applied on the client so the summary counts stay stable", () => {
    expect(apiQuery({ buyerId: "b", status: "RED" })).toEqual({ buyerId: "b", unitId: undefined, shipWeek: undefined, q: undefined });
  });
  it("an empty filter set yields an empty query string", () => {
    expect(toParams({}).toString()).toBe("");
  });
});

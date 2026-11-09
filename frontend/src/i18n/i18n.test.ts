import { describe, expect, it } from "vitest";
import "./app";
import { dictionaries, translate } from "./t";

describe("i18n", () => {
  it("en and ta have identical key sets", () => {
    const en = Object.keys(dictionaries.en).sort();
    const ta = Object.keys(dictionaries.ta).sort();
    expect(ta).toEqual(en);
  });

  it("no empty strings", () => {
    for (const lang of ["en", "ta"] as const) {
      for (const [k, v] of Object.entries(dictionaries[lang])) expect(v.trim(), `${lang}:${k}`).not.toBe("");
    }
  });

  it("placeholders match between languages", () => {
    const ph = (s: string) => (s.match(/\{\w+\}/g) ?? []).sort().join(",");
    for (const k of Object.keys(dictionaries.en)) expect(ph(dictionaries.ta[k]), k).toBe(ph(dictionaries.en[k]));
  });

  it("interpolates and falls back to the key", () => {
    expect(translate("en", "sup.signInAgain", { n: 2 })).toBe("Sign in again to send 2 updates.");
    expect(translate("ta", "does.not.exist")).toBe("does.not.exist");
  });

  it("api error codes all have a message", () => {
    for (const c of ["validation", "unauthenticated", "forbidden", "not_found", "conflict", "rate_limited", "server"])
      expect(dictionaries.en[`err.${c}`]).toBeTruthy();
  });
});

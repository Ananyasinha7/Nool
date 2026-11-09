import { describe, expect, it } from "vitest";
import { fitSize } from "./compress";

describe("photo sizing", () => {
  it("scales the long side to 1280", () => { expect(fitSize(4000, 3000)).toEqual({ w: 1280, h: 960 }); expect(fitSize(3000, 4000)).toEqual({ w: 960, h: 1280 }); });
  it("never upscales", () => { expect(fitSize(800, 600)).toEqual({ w: 800, h: 600 }); });
});

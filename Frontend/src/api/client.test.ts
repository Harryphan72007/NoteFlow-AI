import { describe, expect, it } from "vitest";

import { normalizeAsrLanguage } from "./client";

describe("normalizeAsrLanguage", () => {
  it("maps supported locale variants to backend language names", () => {
    expect(normalizeAsrLanguage("EN-US")).toBe("English");
    expect(normalizeAsrLanguage("vi")).toBe("Vietnamese");
  });

  it("preserves unknown values", () => {
    expect(normalizeAsrLanguage("Klingon")).toBe("Klingon");
  });
});

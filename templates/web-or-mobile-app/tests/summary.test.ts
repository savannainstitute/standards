import { describe, expect, it } from "vitest";

import { parseHeights, summarize } from "../src/summary";
import heightsCsv from "./fixtures/heights.csv?raw";

describe("parseHeights", () => {
  it("reads the height column of the fixture in row order", () => {
    // The fixture's four rows carry 120, 135, 150 and 195 in height_cm.
    expect(parseHeights(heightsCsv)).toEqual([120, 135, 150, 195]);
  });

  it("finds the column wherever the header puts it", () => {
    // height_cm is the first column here, so the values are 80 and 90.
    expect(parseHeights("height_cm,tree_id\n80,T1\n90,T2")).toEqual([80, 90]);
  });

  it("refuses a blank height and names the file row", () => {
    // The blank is on the third line of the text, counting the header as 1.
    expect(() => parseHeights("tree_id,height_cm\nT1,120\nT2,")).toThrow(
      "row 3: height_cm is blank or no number",
    );
  });

  it("refuses a height that is no number", () => {
    // "tall" sits on the second line of the text.
    expect(() => parseHeights("tree_id,height_cm\nT1,tall")).toThrow(
      "row 2: height_cm is blank or no number",
    );
  });

  it("refuses text with no height column", () => {
    expect(() => parseHeights("tree_id,dbh_cm\nT1,4")).toThrow(
      "the header row has no height_cm column",
    );
  });
});

describe("summarize", () => {
  it("summarizes the fixture", () => {
    const summary = summarize(parseHeights(heightsCsv));
    // Four rows in the fixture.
    expect(summary.count).toBe(4);
    // 120 + 135 + 150 + 195 = 600, and 600 / 4 = 150.
    expect(summary.mean).toBe(150);
    // 120 is the smallest of the four and 195 the largest.
    expect(summary.min).toBe(120);
    expect(summary.max).toBe(195);
  });

  it("refuses an empty list", () => {
    expect(() => summarize([])).toThrow("no values to summarize");
  });
});

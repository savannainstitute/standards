import { readFile } from "node:fs/promises";

import { describe, expect, it } from "vitest";

import { showSummary, textReader } from "../src/page";

const fixture = () =>
  readFile(new URL("./fixtures/heights.csv", import.meta.url), "utf8");

describe("showSummary", () => {
  it("writes the summary of the heights file into the element", async () => {
    const output = { textContent: null as string | null };
    const requested: string[] = [];
    await showSummary(output, async (path) => {
      requested.push(path);
      return fixture();
    });
    expect(requested).toEqual(["heights.csv"]);
    // The fixture's heights 120, 135, 150 and 195 sum to 600, so the mean is 150.
    expect(output.textContent).toBe(
      "4 trees, mean height 150 cm, shortest 120 cm, tallest 195 cm",
    );
  });
});

describe("textReader", () => {
  it("returns the body of a response that succeeded", async () => {
    const text = await fixture();
    const read = textReader(async () => new Response(text));
    expect(await read("heights.csv")).toBe(text);
  });

  it("refuses a response that failed and names the path and status", async () => {
    const read = textReader(async () => new Response("", { status: 404 }));
    await expect(read("heights.csv")).rejects.toThrow(
      "heights.csv could not be read: status 404",
    );
  });
});

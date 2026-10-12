/** Page entry: fetch the heights file from public/ and show its summary. */
import { parseHeights, summarize } from "./summary";

const output = document.querySelector<HTMLElement>("#summary");
if (output === null) {
  throw new Error("index.html has no element with the id summary");
}

const response = await fetch("heights.csv");
if (!response.ok) {
  throw new Error(`heights.csv could not be read: status ${response.status}`);
}

const summary = summarize(parseHeights(await response.text()));
output.textContent =
  `${summary.count} trees, mean height ${summary.mean} cm, ` +
  `shortest ${summary.min} cm, tallest ${summary.max} cm`;

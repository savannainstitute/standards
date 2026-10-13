/** Page entry: show the heights file's summary in the element with the id summary. */
import { showSummary, textReader } from "./page";

const output = document.querySelector<HTMLElement>("#summary");
if (output === null) {
  throw new Error("index.html has no element with the id summary");
}
await showSummary(output, textReader(fetch));

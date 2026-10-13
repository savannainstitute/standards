/** The page's one job: read the heights file and write its summary into an element. */
import { parseHeights, summarize } from "./summary";

/** Return a reader that fetches a path and refuses a response that failed. */
export function textReader(
  fetchPath: (path: string) => Promise<Response>,
): (path: string) => Promise<string> {
  return async (path) => {
    const response = await fetchPath(path);
    if (!response.ok) {
      throw new Error(`${path} could not be read: status ${response.status}`);
    }
    return response.text();
  };
}

/** Write the summary of the heights CSV into the element's text. */
export async function showSummary(
  output: { textContent: string | null },
  readText: (path: string) => Promise<string>,
): Promise<void> {
  const summary = summarize(parseHeights(await readText("heights.csv")));
  output.textContent =
    `${summary.count} trees, mean height ${summary.mean} cm, ` +
    `shortest ${summary.min} cm, tallest ${summary.max} cm`;
}

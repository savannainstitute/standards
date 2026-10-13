/** Height summary for one plot: pure functions that touch neither the page nor the network. */

export interface Summary {
  count: number;
  mean: number;
  min: number;
  max: number;
}

/**
 * Read the height_cm column from CSV text whose first row is the header.
 * A missing column, a blank height or a height that is no number is an error.
 */
export function parseHeights(csvText: string): number[] {
  const [header, ...rows] = csvText.trim().split(/\r?\n/);
  const column = header.split(",").indexOf("height_cm");
  if (column === -1) {
    throw new Error("the header row has no height_cm column");
  }
  return rows.map((row, index) => {
    const cell = row.split(",")[column];
    const height = Number(cell);
    if (cell === undefined || cell.trim() === "" || !Number.isFinite(height)) {
      throw new Error(`row ${index + 2}: height_cm is blank or no number`);
    }
    return height;
  });
}

/** Count, mean, smallest and largest of the values; an empty list is an error. */
export function summarize(values: number[]): Summary {
  if (values.length === 0) {
    throw new Error("no values to summarize");
  }
  const total = values.reduce((sum, value) => sum + value, 0);
  return {
    count: values.length,
    mean: total / values.length,
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

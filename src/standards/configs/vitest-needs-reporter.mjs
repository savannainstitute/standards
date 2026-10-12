/** vitest reporter: print how many tests the needs marker left out, and why. */

const NEEDS_TAG = / \[needs (.+)\]$/;

export default class NeedsReporter {
  /** After the run, count the skipped tests whose name carries a needs tag. */
  onTestRunEnd(testModules) {
    const reasons = [];
    for (const testModule of testModules) {
      for (const testCase of testModule.children.allTests("skipped")) {
        const tag = NEEDS_TAG.exec(testCase.name);
        if (tag !== null) {
          reasons.push(tag[1]);
        }
      }
    }
    if (reasons.length > 0) {
      const unique = [...new Set(reasons)].sort();
      console.log(
        `\n${reasons.length} test(s) left out because they need: ${unique.join("; ")}`,
      );
    }
  }
}

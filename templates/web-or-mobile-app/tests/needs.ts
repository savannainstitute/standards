/** The needs marker: a test the hosted check cannot run says what it needs. */
import { it } from "vitest";

type TestBody = () => void | Promise<void>;

/**
 * Return a function that registers a test under the name and the reason.
 * The test is left out when STANDARDS_NO_NEEDS is true and runs otherwise.
 */
export function needs(reason: string) {
  if (reason.trim() === "") {
    throw new Error("needs() requires a reason");
  }
  const leftOut = process.env.STANDARDS_NO_NEEDS === "true";
  return (name: string, body: TestBody) =>
    it.skipIf(leftOut)(`${name} [needs ${reason}]`, body); // the needs() reason, printed by the reporter
}

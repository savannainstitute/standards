"""Render docs/RULES.md from the rule list, or check that it is current.

Usage: render-rules [--check]
"""

import argparse
import sys
from pathlib import Path

from standards.markdown_wrap import fill
from standards.rules import RULES

INTRO = [
    "This reference documents the organization-specific automated checks "
    "proposed for Savanna Institute repositories. Initial feedback is due "
    "November 13, 2026. Staged migration begins December 4, 2026; all "
    "active organization repositories must comply with the standards by "
    "March 5, 2027. Feedback continues during migration and afterward.",
    "Under the proposed migration process, required checks are activated "
    "with each owner during migration, "
    "after the setup is verified. Each repository is checked in full after "
    "its initial cleanup; rules identified as change-specific inspect the "
    "pull request's changes. The same requirements apply to all authors, "
    "including work produced with coding agents.",
    "Blocking findings fail the check and prevent merging. Advisory "
    "findings are warnings for review and do not fail the check. Each "
    "entry gives the rule ID reported in the log, its scope, the "
    "requirement, and the corrective action. Examples illustrate detected "
    "patterns; they are not an exhaustive specification.",
    "The shared workflow also runs language-specific formatting, static "
    "analysis, tests, coverage checks, and secret scanning. Those tools "
    "can fail independently of the rules below. See "
    "[CONTRIBUTING](https://github.com/savannainstitute/"
    ".github/blob/main/CONTRIBUTING.md) "
    "for the pull request process and handling failed checks.",
    "The rule entries describe the proposed release. Existing installations "
    "may still follow the standards main branch with separate local hook "
    "revisions. During migration, install a validated release as a complete "
    "bundle. The revised daily monitor reports usage and drift without "
    "disabling workflows, reactivating them, or enabling required checks. "
    "Deployment requires release validation and owner coordination. "
    "Existing protections remain in effect.",
    "Coverage reports identify untested lines. Numeric coverage targets "
    "are optional and repository-specific, recorded with a rationale in "
    "the selected standards release. Configured targets block on "
    "insufficient coverage or missing measurements. Failed tests block "
    "independently of coverage targets. See "
    "[coverage policy configuration]"
    "(../overrides/README.md#coverage-targets).",
    "Scientific validation is a review responsibility described in "
    "CONTRIBUTING. Automated tests and coverage cannot establish that a "
    "method, reference result, or scientific interpretation is correct.",
    "American English applies to project-authored prose. Preserve external "
    "identifiers, data values, quotations, and reference titles. The current "
    "spelling check excludes inline backtick literals and Markdown block "
    "quotations. Other false positives remain possible; findings are "
    "advisory. Report incorrect findings rather than changing "
    "required literals. A warning does not require a change to an external "
    "interface or scientific meaning.",
]


def wrap(paragraph):
    """Return the paragraph filled to the Markdown width and a blank line."""
    return fill(paragraph) + "\n\n"


def render():
    """Return the Markdown text of the rule list."""
    parts = [
        "# Automated check reference\n\n",
        *(wrap(paragraph) for paragraph in INTRO),
    ]
    parts.append("## Feedback\n\n")
    parts.append(
        wrap(
            "Report feedback through a standards "
            "[issue](https://github.com/savannainstitute/"
            "standards/issues/new) "
            "or contact Zack directly. Identify the rule ID, "
            "the affected work, "
            "and the practical effect: useful requirements, unclear wording, "
            "unnecessary effort, incorrect findings, or blocked work. Include "
            "an example and an alternative where possible, and state any "
            "deadline. Send sensitive examples directly. "
            "Submit initial feedback "
            "by November 13, 2026. Continue reporting problems during "
            "migration and after the March 5, 2027 compliance deadline."
        )
    )
    for heading, blocks in (
        ("Blocking requirements", True),
        ("Advisory findings", False),
    ):
        parts.append(f"## {heading}\n\n")
        for rule in RULES:
            if rule.blocks != blocks:
                continue
            parts.append(f"### {rule.id}\n\n")
            parts.append(wrap(f"Scope: {rule.scope}."))
            parts.append(wrap(rule.rule + " " + rule.fix))
            if rule.examples:
                parts.append("```text\n")
                parts.extend(f"{example}\n" for example in rule.examples)
                parts.append("```\n\n")
    parts.append("## Maintaining this reference\n\n")
    parts.append(
        wrap(
            "The rule descriptions are generated from "
            "`src/standards/rules.py` using `render-rules`. "
            "Update that source and regenerate this file "
            "when revising a rule description."
        )
    )
    return "".join(parts).rstrip("\n") + "\n"


def target(root):
    """Path of the rendered file inside the standards checkout at root."""
    return Path(root) / "docs" / "RULES.md"


def main(argv=None):
    """Write the file, or with --check exit 1 if it is stale."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if docs/RULES.md is stale"
    )
    parser.add_argument(
        "--root", default=".", help="the standards repo checkout"
    )
    args = parser.parse_args(argv)
    path = target(args.root)
    text = render()
    if args.check:
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        if current != text:
            print(f"{path} is stale; run render-rules")
            return 1
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

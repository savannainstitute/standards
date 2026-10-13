"""Render docs/RULES.md from the rule list, or check that it is current.

Usage: render-rules [--check]
"""

import argparse
import sys
import textwrap
from pathlib import Path

from standards.rules import RULES

HEADER = """# The rules

Every repository in the organization is checked against this list on every
pull request. A rule that blocks fails the check, and the pull request cannot
merge until it passes. A rule that warns prints its finding for the author
and the reviewer and does not fail the check.

This file is generated from the rule list in `src/standards/rules.py`; edit
that file and run `render-rules`.

"""


def wrap(paragraph):
    """Return the paragraph wrapped to the header's width and a blank line."""
    lines = textwrap.fill(
        paragraph, width=79, break_long_words=False, break_on_hyphens=False
    )
    return lines + "\n\n"


def render():
    """Return the Markdown text of the rule list."""
    parts = [HEADER]
    for rule in RULES:
        severity = "Blocks" if rule.blocks else "Warns"
        parts.append(f"## {rule.id}\n\n")
        parts.append(wrap(f"{severity}. Looks at {rule.scope}."))
        parts.append(wrap(rule.rule))
        parts.append(wrap(f"To fix it: {rule.fix}"))
        if rule.examples:
            parts.append("Shapes the check looks for:\n\n```text\n")
            parts.extend(f"{example}\n" for example in rule.examples)
            parts.append("```\n\n")
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

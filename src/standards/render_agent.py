"""Render the agent files from the rule list, or check they are current.

Usage: render-agent [--check] [--root DIR]

AGENTS.md and the hook's pattern file are rendered from the rule list and
the check's own patterns, then every agent file is copied to the root of the
standards checkout and into each folder under templates/. With --check
nothing is written and the exit code is 1 when any file is stale.
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

from standards import agent_files, rules_check
from standards.rules import RULES

# The Python line length in configs/ruff.toml, so one width serves the repo.
WIDTH = 79
RULES_URL = (
    "https://github.com/savannainstitute/standards/blob/v1/docs/RULES.md"
)

HEADER = f"""# Rules for coding agents

Every pull request in this repository runs the organization's check, which
appears as `checks / lint` and blocks the merge when it fails. The rules
below are that check's list, with the same ids its findings print. The full
list with every shape the check looks for is at
<{RULES_URL}>.

## Before you commit

- Run `pre-commit run --all-files`. It runs the same check on this
  computer. Fix each finding it prints; do not silence it.
- This repository holds no linter settings. They live in the organization's
  standards repository, and a settings file added here is ignored.
- Write commit messages and pull request text that say what the change
  does. Add no tool attribution: no co-author trailer and no generated-with
  line.
- The pull request text is read by the check. A new dependency is named on
  a `Dependencies:` line. A new Markdown file outside the docs folder is
  listed under a `Docs added` heading. A removed test is listed under a
  `Tests removed or skipped` heading. A source change with no test carries a
  `No test because` line.
- A test the hosted check cannot run is marked with what it needs, such as
  `@pytest.mark.needs("a GPU")`. A bare skip is refused.
- A test asserts on a value computed from a planted input, and the comment
  beside the expected value derives it.
"""


def render_rule(rule):
    """Return the Markdown list item for one rule."""
    item = textwrap.fill(
        f"- `{rule.id}`: {rule.rule} To fix it: {rule.fix}",
        width=WIDTH,
        subsequent_indent="  ",
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not rule.examples:
        return item + "\n"
    shapes = "".join(f"  {example}\n" for example in rule.examples)
    return f"{item}\n\n  ```text\n{shapes}  ```\n"


def render_agents():
    """Return the text of AGENTS.md."""
    parts = [HEADER]
    for heading, blocks in (
        ("Rules that block the merge", True),
        ("Rules that warn", False),
    ):
        parts.append(f"\n## {heading}\n\n")
        chosen = [rule for rule in RULES if rule.blocks == blocks]
        parts.append("\n".join(render_rule(rule) for rule in chosen))
    parts.append(f"\n{agent_files.MARKER}\n")
    return "".join(parts)


def render_patterns():
    """Return the JSON text of the patterns the hook reads."""
    data = {
        "characters": rules_check.EM_DASH_OR_CURLY.pattern,
        "emoji": rules_check.EMOJI.pattern,
        "bold": rules_check.BOLD.pattern,
        "caps_token": rules_check.CAPS_TOKEN.pattern,
        "emphasis_words": sorted(rules_check.EMPHASIS_WORDS),
        "glued_before": rules_check.GLUED_BEFORE,
        "glued_after": rules_check.GLUED_AFTER,
        "contrast": [p.pattern for p in rules_check.CONTRAST],
        "sales": rules_check.SALES.pattern,
        "narration": rules_check.NARRATION.pattern,
        "divider": rules_check.DIVIDER.pattern,
        "code_suffixes": sorted(rules_check.CODE_SUFFIXES),
        "markdown_suffixes": sorted(rules_check.MARKDOWN_SUFFIXES),
        "config_suffixes": sorted(rules_check.CONFIG_SUFFIXES),
        "slash_suffixes": sorted(rules_check.SLASH_COMMENT_SUFFIXES),
    }
    return json.dumps(data, indent=2) + "\n"


RENDERED = {"AGENTS.md": render_agents, "rules_hook.json": render_patterns}


def destinations(root):
    """Return the standards checkout root and each template folder."""
    templates = Path(root) / "templates"
    return [Path(root), *sorted(p for p in templates.iterdir() if p.is_dir())]


def stale_files(root):
    """Return every rendered file or copy under root that is not current."""
    stale = []
    for name, render in RENDERED.items():
        path = agent_files.canonical(name)
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        if current != render():
            stale.append(str(path))
    for destination in destinations(root):
        stale.extend(
            str(destination / path)
            for path in agent_files.compare(destination)
        )
    return stale


def main(argv=None):
    """Write every agent file, or with --check exit 1 if any is stale."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if any file is stale"
    )
    parser.add_argument(
        "--root", default=".", help="the standards repo checkout"
    )
    args = parser.parse_args(argv)
    if args.check:
        stale = stale_files(args.root)
        for path in stale:
            print(f"{path} is stale; run render-agent")
        return 1 if stale else 0
    for name, render in RENDERED.items():
        agent_files.canonical(name).write_text(
            render(), encoding="utf-8", newline="\n"
        )
    for destination in destinations(args.root):
        agent_files.write_copies(destination)
        print(f"wrote the agent files under {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""The agent files every repository carries, and where each one sits.

The organization's copy of each file ships inside this package under agent/.
A repository holds a copy at the path named in COPIES. AGENTS.md and
CLAUDE.md end with a marker line; a repository may add its own notes below
it, and only the text up to the marker is compared.
"""

from importlib import resources
from pathlib import Path

MARKER = "<!-- Organization copy above; this repository's notes go below. -->"
COPIES = {
    "AGENTS.md": "AGENTS.md",
    "CLAUDE.md": "CLAUDE.md",
    "claude_settings.json": ".claude/settings.json",
    "gemini_settings.json": ".gemini/settings.json",
    "rules_hook.py": ".claude/hooks/rules_hook.py",
    "rules_hook.json": ".claude/hooks/rules_hook.json",
}


def canonical(name):
    """Return the path of the organization's copy of one agent file."""
    return Path(str(resources.files("standards").joinpath("agent", name)))


def above_marker(text):
    """Return the text up to and including the marker line."""
    head, found, _ = text.partition(MARKER)
    return head + found if found else text


def compare(repo_dir):
    """Return the repository paths that are missing or differ, sorted."""
    stale = []
    for name, repo_path in COPIES.items():
        expected = canonical(name).read_text(encoding="utf-8")
        copy = Path(repo_dir) / repo_path
        if not copy.is_file():
            stale.append(repo_path)
            continue
        actual = copy.read_text(encoding="utf-8")
        if MARKER in expected:
            expected, actual = above_marker(expected), above_marker(actual)
        if actual.rstrip("\n") != expected.rstrip("\n"):
            stale.append(repo_path)
    return sorted(stale)


def write_copies(repo_dir):
    """Write every agent file into the repository, keeping its own notes."""
    for name, repo_path in COPIES.items():
        text = canonical(name).read_text(encoding="utf-8")
        copy = Path(repo_dir) / repo_path
        if MARKER in text and copy.is_file():
            _, found, notes = copy.read_text(encoding="utf-8").partition(
                MARKER
            )
            if found:
                text = above_marker(text) + notes
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_text(text, encoding="utf-8", newline="\n")

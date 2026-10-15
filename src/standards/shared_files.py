"""Compare a repository's copies of the shared files with this package's.

A repository carries the caller workflow and the agent files copied from the
standards repository, and a pre-commit configuration that runs the standards
hooks at the same immutable commit as the workflow. findings() names each one
that is missing or out of date and says how to bring it back in line.
"""

import re
import subprocess
from importlib import resources
from pathlib import Path

import yaml

from standards import agent_files

HOOKS_URL = "https://github.com/savannainstitute/standards"
CALLER_PATH = ".github/workflows/checks.yml"
PRE_COMMIT_PATH = ".pre-commit-config.yaml"
# Template seed; release adoption replaces it with the selected bundle commit.
TEMPLATE_REV = "049d382a82f39372474d45310f682ab6170c0f0c"


def caller_text(revision=None):
    """Return the text of the caller workflow every repository carries."""
    path = resources.files("standards").joinpath("configs", "caller.yml")
    text = path.read_text(encoding="utf-8")
    return re.sub(
        r"(checks\.yml@)[^\s]+", r"\g<1>" + (revision or TEMPLATE_REV), text
    )


def caller_revision(text):
    """Return an immutable standards workflow revision, or None."""
    match = re.search(
        r"uses: savannainstitute/standards/\.github/workflows/"
        r"checks\.yml@([0-9a-f]{40})(?=\s|$)",
        text,
    )
    return match.group(1) if match else None


def pre_commit_rev(repo_dir):
    """Return the rev the repository pins the shared hooks at, or None."""
    config = Path(repo_dir) / PRE_COMMIT_PATH
    if not config.is_file():
        return None
    data = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    for entry in data.get("repos") or []:
        if str(entry.get("repo")).rstrip("/") == HOOKS_URL:
            return str(entry.get("rev"))
    return None


def findings(repo_dir, revision=None):
    """Return (path, message) for each copy that is missing or differs."""
    found = []
    caller = Path(repo_dir) / CALLER_PATH
    text = caller.read_text(encoding="utf-8") if caller.is_file() else ""
    selected = caller_revision(text)
    expected = revision or selected or TEMPLATE_REV
    if (
        not caller.is_file()
        or selected is None
        or text.rstrip() != caller_text(expected).rstrip()
    ):
        found.append(
            (
                CALLER_PATH,
                f"Copy {CALLER_PATH} from the template for this kind of "
                "project in the standards repository, unchanged.",
            )
        )
    if pre_commit_rev(repo_dir) != expected:
        found.append(
            (
                PRE_COMMIT_PATH,
                f"Use the workflow revision {expected} for the hooks from "
                f"{HOOKS_URL} in {PRE_COMMIT_PATH}.",
            )
        )
    found.extend(
        (
            path,
            f"Copy {path} from the template for this kind of project in "
            "the standards repository; text below the marker line in "
            "AGENTS.md and CLAUDE.md is yours to keep.",
        )
        for path in agent_files.compare(repo_dir)
    )
    named = {path for path, _ in found}
    tracked = set(
        subprocess.run(
            ["git", "-C", str(repo_dir), "ls-files", "--cached"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.splitlines()
    )
    shared = [CALLER_PATH, PRE_COMMIT_PATH, *agent_files.COPIES.values()]
    found.extend(
        (
            path,
            f"{path} is in the folder but git does not track it; remove the "
            "line in .gitignore that ignores it and commit it.",
        )
        for path in sorted(shared)
        if path not in named
        and path not in tracked
        and (Path(repo_dir) / path).is_file()
    )
    return found


def write_copies(repo_dir, revision=None):
    """Write current copies of every shared file into the repository."""
    revision = revision or TEMPLATE_REV
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("standards revision must be a full commit SHA")
    agent_files.write_copies(repo_dir)
    caller = Path(repo_dir) / CALLER_PATH
    caller.parent.mkdir(parents=True, exist_ok=True)
    caller.write_text(caller_text(revision), encoding="utf-8", newline="\n")
    config = {
        "repos": [
            {
                "repo": HOOKS_URL,
                "rev": revision,
                "hooks": [{"id": "rules-check"}],
            }
        ]
    }
    (Path(repo_dir) / PRE_COMMIT_PATH).write_text(
        yaml.safe_dump(config, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )

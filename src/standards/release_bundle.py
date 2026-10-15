"""Install a standards bundle from one immutable commit in a local checkout."""

import argparse
import re
import subprocess
from pathlib import Path

import yaml

from standards import agent_files, shared_files


def read_at(root, revision, path):
    """Read a tracked file at the selected commit without checking it out."""
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{revision}:{path}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def resolve(root, revision):
    """Require an existing full commit SHA, never a moving branch or tag."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("standards revision must be a full commit SHA")
    actual = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "rev-parse",
            "--verify",
            revision + "^{commit}",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual != revision:
        raise ValueError("revision must identify a commit directly")
    return actual


def bundle(root, revision):
    """Read and validate the complete bundle before changing any files."""
    resolve(root, revision)
    read_at(root, revision, ".github/workflows/checks.yml")
    caller = read_at(root, revision, "src/standards/configs/caller.yml")
    caller, count = re.subn(
        r"(checks\.yml@)[^\s]+", r"\g<1>" + revision, caller
    )
    if count != 1:
        raise ValueError(
            "release must contain one standards workflow reference"
        )
    files = {shared_files.CALLER_PATH: caller}
    for name, path in agent_files.COPIES.items():
        files[path] = read_at(root, revision, f"src/standards/agent/{name}")
    config = read_at(
        root,
        revision,
        "templates/documentation-and-configuration/.pre-commit-config.yaml",
    )
    files[shared_files.PRE_COMMIT_PATH] = config
    return files


def apply(repo_dir, standards_root, revision):
    """Adopt or roll back the whole bundle, preserving project agent notes."""
    files = bundle(standards_root, revision)
    repo = Path(repo_dir)
    config_path = repo / shared_files.PRE_COMMIT_PATH
    config = yaml.safe_load(
        config_path.read_text(encoding="utf-8")
        if config_path.is_file()
        else files[shared_files.PRE_COMMIT_PATH]
    )
    entries = [
        entry
        for entry in config["repos"]
        if str(entry.get("repo")).rstrip("/") == shared_files.HOOKS_URL
    ]
    if len(entries) != 1:
        raise ValueError("pre-commit config must contain one standards entry")
    entries[0]["rev"] = revision
    files[shared_files.PRE_COMMIT_PATH] = yaml.safe_dump(
        config, sort_keys=False
    )
    for path, text in files.items():
        target = repo / path
        if agent_files.MARKER in text and target.is_file():
            _, found, notes = target.read_text(encoding="utf-8").partition(
                agent_files.MARKER
            )
            if found:
                text = agent_files.above_marker(text) + notes
        files[path] = text
    for path, text in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")


def main(argv=None):
    """Prepare a local update for review; never commit, push, or merge it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-dir", required=True)
    parser.add_argument("--standards-root", required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args(argv)
    apply(args.repo_dir, args.standards_root, args.revision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

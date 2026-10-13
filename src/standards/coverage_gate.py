"""Fail the check when a repository's test coverage is under the floor.

Usage:
    coverage-gate --report FILE [--report FILE ...] [--repo-dir DIR]
                  [--base SHA] [--head SHA] [--repo OWNER/NAME]
                  [--standards-root DIR]

Each report is a Cobertura XML file, which coverage.py and vitest write. A
repository with no recorded starting value needs the floor in configs/
coverage.yaml. A repository whose starting value is recorded under
overrides/<repo>/coverage.yaml, because it was below the floor when it was
cleaned up, may not fall below that value, and each pull request must cover
the changed-lines share of the code lines it adds, until it reaches the floor.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

import yaml

from standards import rules_check, tools


def settings():
    """Return the floor and the changed-lines share from the shipped file."""
    path = Path(tools.config_path("coverage.yaml"))
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return float(data["floor_percent"]), float(data["changed_lines_percent"])


def repo_path(repo_dir, sources, filename):
    """Return the report's file name as a path relative to the repository."""
    root = Path(repo_dir).resolve()
    for source in sources or ["."]:
        candidate = (root / source / filename).resolve()
        if Path(source).is_absolute():
            candidate = (Path(source) / filename).resolve()
        if candidate.is_relative_to(root):
            return candidate.relative_to(root).as_posix()
    return PurePosixPath(filename).as_posix()


def load_lines(repo_dir, reports):
    """Return {path: {line: hits}} from every Cobertura report."""
    lines = {}
    for report in reports:
        tree = ET.parse(report)
        sources = [s.text.strip() for s in tree.iter("source") if s.text]
        for cls in tree.iter("class"):
            path = repo_path(repo_dir, sources, cls.get("filename"))
            hits = lines.setdefault(path, {})
            for line in cls.iter("line"):
                number = int(line.get("number"))
                count = int(line.get("hits"))
                hits[number] = (
                    max(hits[number], count) if number in hits else count
                )
    return lines


def total(lines):
    """Return (covered, measured) over every measured line."""
    counts = [hits for path in lines.values() for hits in path.values()]
    return sum(1 for hits in counts if hits > 0), len(counts)


def changed(lines, added):
    """Return (covered, measured) over the measured lines a change adds."""
    covered = measured = 0
    for path, numbers in added.items():
        if path not in lines:
            continue
        hits = lines[path]
        for number in numbers:
            if number in hits:
                measured += 1
                covered += hits[number] > 0
    return covered, measured


def percent(covered, measured):
    """Return the share as a percentage, one decimal place."""
    return round(100 * covered / measured, 1) if measured else 100.0


def decide(repo_percent, start, changed_counts):
    """Return (passes, message) for the repository and its change."""
    floor, changed_floor = settings()
    if repo_percent >= floor:
        return True, f"Coverage is {repo_percent}%, at or above {floor:g}%."
    if start is None:
        return False, (
            f"Coverage is {repo_percent}%; a repository needs {floor:g}%. "
            "Add tests for the files in the table above with the most "
            "uncovered lines."
        )
    if repo_percent < start:
        return False, (
            f"Coverage is {repo_percent}%, below the {start}% recorded "
            "for this repository; add tests until it is back."
        )
    covered, measured = changed_counts
    if not measured:
        return True, (
            f"Coverage is {repo_percent}%, not below {start}%, and no "
            "changed line is code the tests measure."
        )
    share = percent(covered, measured)
    if share < changed_floor:
        return False, (
            f"Tests cover {share}% of the changed lines; until the repository "
            f"reaches {floor:g}%, each pull request covers "
            f"{changed_floor:g}% of the code it changes."
        )
    return True, (
        f"Coverage is {repo_percent}%, not below {start}%, and tests cover "
        f"{share}% of the changed lines."
    )


def recorded_start(standards_root, repo_name):
    """Return the starting value recorded for the repository, or None."""
    file = rules_check.override_file(
        standards_root, repo_name, "coverage.yaml"
    )
    if file is None:
        return None
    data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
    if not str(data.get("measured_at_commit") or "").strip():
        raise SystemExit(f"{file}: start_percent needs measured_at_commit")
    return float(data["start_percent"])


def main(argv=None):
    """Command line entry point; returns 1 when coverage is under the floor."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--report", action="append", required=True)
    parser.add_argument("--repo-dir", default=".")
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo")
    parser.add_argument("--standards-root")
    args = parser.parse_args(argv)
    reports = [r for r in args.report if Path(r).is_file()]
    if not reports:
        print("No coverage report was written; nothing to measure.")
        return 0
    lines = load_lines(args.repo_dir, reports)
    repo_percent = percent(*total(lines))
    start = recorded_start(args.standards_root, args.repo)
    added = {}
    if args.base:
        diff = rules_check.parse_diff(args.repo_dir, args.base, args.head)
        added = {
            path: [n for n, _ in change["added"]]
            for path, change in diff.items()
        }
    passes, message = decide(repo_percent, start, changed(lines, added))
    print(message)
    return 0 if passes else 1


if __name__ == "__main__":
    sys.exit(main())

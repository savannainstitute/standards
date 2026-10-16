"""Report coverage and enforce centrally reviewed repository targets.

Usage:
    coverage-gate --report FILE [--report FILE ...] [--repo-dir DIR]
                  [--base SHA] [--head SHA] [--repo OWNER/NAME]
                  [--standards-root DIR]

Cobertura reports measure executed lines. Repository targets and rationale
live in overrides/<repo>/coverage.yaml in the selected standards release.
"""

import argparse
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

import yaml

from standards import rules_check, tools


def settings():
    """Return the shared reporting defaults."""
    path = Path(tools.config_path("coverage.yaml"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def policy(standards_root, repo_name):
    """Load and validate targets from the selected standards release."""
    data = settings()
    file = rules_check.override_file(
        standards_root, repo_name, "coverage.yaml"
    )
    if file is None:
        return data
    override = yaml.safe_load(file.read_text(encoding="utf-8"))
    allowed = {
        "floor_percent",
        "changed_lines_percent",
        "rationale",
        "start_percent",
        "measured_at_commit",
    }
    if not isinstance(override, dict) or set(override) - allowed:
        raise SystemExit(f"{file}: invalid coverage policy fields")
    if "start_percent" in override:
        if override["start_percent"] is None:
            raise SystemExit(f"{file}: start_percent needs a numeric value")
        if "floor_percent" in override:
            raise SystemExit(f"{file}: specify start_percent or floor_percent")
        if not str(override.get("measured_at_commit") or "").strip():
            raise SystemExit(f"{file}: start_percent needs measured_at_commit")
        override["floor_percent"] = override["start_percent"]
    elif not str(override.get("rationale") or "").strip():
        raise SystemExit(f"{file}: coverage targets need a rationale")
    for key in ("floor_percent", "changed_lines_percent"):
        value = override.get(key)
        if value is not None:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0 <= value <= 100
            ):
                raise SystemExit(f"{file}: {key} must be between 0 and 100")
    data.update(override)
    return data


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


def decide(repo_percent, targets, changed_counts):
    """Return (passes, message) for explicitly configured targets."""
    floor = targets.get("floor_percent")
    changed_floor = targets.get("changed_lines_percent")
    if floor is not None and repo_percent < floor:
        return False, (
            f"Coverage is {repo_percent}%, below this repository's "
            f"{floor:g}% target."
        )
    if changed_floor is not None and changed_counts is not None:
        covered, measured = changed_counts
        if measured and 100 * covered / measured < changed_floor:
            return False, (
                f"Tests cover {percent(covered, measured)}% of changed lines; "
                f"this repository requires {changed_floor:g}%."
            )
    if floor is None and changed_floor is None:
        return True, (
            f"Coverage is {repo_percent}%; reporting only. Review untested "
            "behavior and scientific validation evidence."
        )
    message = f"Coverage is {repo_percent}%; configured targets pass."
    if changed_floor is not None and changed_counts is None:
        message += " Changed-line target applies to pull requests with a base."
    return True, message


def main(argv=None):
    """Report coverage; return 1 for unmet targets or missing measurements."""
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
    targets = policy(args.standards_root, args.repo)
    enforced = any(
        targets.get(key) is not None
        for key in ("floor_percent", "changed_lines_percent")
    )
    reports = [r for r in args.report if Path(r).is_file()]
    if not reports:
        print("No coverage report was written; nothing to measure.")
        return 1 if enforced else 0
    lines = load_lines(args.repo_dir, reports)
    covered, measured = total(lines)
    if not measured:
        print("Coverage report contains no measured lines.")
        return 1 if enforced else 0
    repo_percent = 100 * covered / measured
    added = {}
    if args.base:
        diff = rules_check.parse_diff(args.repo_dir, args.base, args.head)
        added = {
            path: [n for n, _ in change["added"]]
            for path, change in diff.items()
        }
    changed_counts = changed(lines, added) if args.base else None
    passes, message = decide(repo_percent, targets, changed_counts)
    print(message)
    return 0 if passes else 1


if __name__ == "__main__":
    sys.exit(main())

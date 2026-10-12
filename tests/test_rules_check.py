"""The slop check reports exactly the planted findings, and nothing else."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from standards import rules_check, standards_copy

FIXTURES = Path(__file__).parent / "fixtures"
STANDARDS_ROOT = Path(__file__).parents[1]


def git(repo, *args):
    env = dict(
        os.environ,
        GIT_AUTHOR_NAME="t",
        GIT_AUTHOR_EMAIL="t@example.org",
        GIT_COMMITTER_NAME="t",
        GIT_COMMITTER_EMAIL="t@example.org",
    )
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    ).stdout.strip()


def write_tree(repo, tree):
    for path, content in tree.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")


def build(repo, scenario):
    """Build the scenario as a git repo; return (base sha, head sha, body)."""
    git(repo, "init", "-q", "-b", "main")
    if scenario.get("with_standards_copies"):
        standards_copy.write_copies(repo)
    write_tree(repo, scenario["base"])
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Base")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "change")
    for path in scenario["base"]:
        if path not in scenario["head"]:
            (repo / path).unlink()
    write_tree(repo, scenario["head"])
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", scenario["commit_message"])
    head = git(repo, "rev-parse", "HEAD")
    body = repo.parent / "body.txt"
    body.write_text(scenario["pr_body"], encoding="utf-8", newline="\n")
    return base, head, body


def load(name):
    scenario = json.loads(
        (FIXTURES / f"planted_{name}.json").read_text(encoding="ascii")
    )
    expected = {
        tuple(row)
        for row in json.loads((FIXTURES / f"expected_{name}.json").read_text())
    }
    return scenario, expected


def findings_for(tmp_path, scenario, standards_root):
    repo = tmp_path / "repo"
    repo.mkdir()
    base, head, body = build(repo, scenario)
    findings = rules_check.run(
        repo,
        base=base,
        head=head,
        pr_body=body.read_text(encoding="utf-8"),
        repo_name="savannainstitute/planted",
        standards_root=standards_root,
    )
    return {(f.rule, f.path, f.line) for f in findings}


@pytest.mark.parametrize("name", ["a", "b"])
def test_planted_findings(tmp_path, name):
    scenario, expected = load(name)
    actual = findings_for(tmp_path, scenario, STANDARDS_ROOT)
    assert actual == expected, (
        f"unexpected: {sorted(actual - expected)}\n"
        f"missing: {sorted(expected - actual)}"
    )


def test_every_rule_is_planted():
    """Every rule in the list appears in one of the two expected files."""
    planted = set()
    for name in ("a", "b"):
        planted |= {row[0] for row in load(name)[1]}
    assert planted == set(rules_check.rules.BY_ID)


def test_exempt_entry_removes_only_its_rule_on_its_path(tmp_path):
    """An exempt.yaml entry for README.md drops readme-path there only."""
    scenario, expected = load("a")
    override = tmp_path / "standards" / "overrides" / "planted"
    override.mkdir(parents=True)
    (override / "exempt.yaml").write_text(
        "exempt:\n"
        "  - path: README.md\n"
        "    rules: [readme-path]\n"
        "    reason: the planted README names files on purpose\n",
        encoding="utf-8",
    )
    actual = findings_for(tmp_path, scenario, tmp_path / "standards")
    assert actual == expected - {("readme-path", "README.md", 3)}


def test_exempt_entry_without_reason_is_refused(tmp_path):
    scenario, _ = load("b")
    override = tmp_path / "standards" / "overrides" / "planted"
    override.mkdir(parents=True)
    (override / "exempt.yaml").write_text(
        "exempt:\n  - path: README.md\n    rules: [readme-path]\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="needs a reason"):
        findings_for(tmp_path, scenario, tmp_path / "standards")


def test_blocking_exit_code(tmp_path):
    scenario, _ = load("b")
    repo = tmp_path / "repo"
    repo.mkdir()
    base, head, body = build(repo, scenario)
    code = rules_check.main(
        [
            "--repo-dir",
            str(repo),
            "--base",
            base,
            "--head",
            head,
            "--pr-body",
            str(body),
            "--repo",
            "savannainstitute/planted",
        ]
    )
    assert code == 1

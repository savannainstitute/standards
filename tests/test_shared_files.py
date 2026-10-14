"""Each shared copy is reported when it drifts, with the fix named."""

import subprocess
from pathlib import Path

import pytest

from standards import shared_files

ROOT = Path(__file__).parents[1]
TEMPLATES = sorted(p for p in (ROOT / "templates").iterdir() if p.is_dir())


def track(repo):
    """Make the folder a git repository and stage everything not ignored."""
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)


def test_current_copies_have_no_findings(tmp_path):
    shared_files.write_copies(tmp_path)
    track(tmp_path)
    assert shared_files.findings(tmp_path) == []


def test_an_ignored_copy_is_named(tmp_path):
    """The planted .gitignore hides the .claude folder and CLAUDE.md."""
    shared_files.write_copies(tmp_path)
    (tmp_path / ".gitignore").write_text("/.claude/\n/CLAUDE.md\n")
    track(tmp_path)
    found = shared_files.findings(tmp_path)
    assert [path for path, _ in found] == [
        ".claude/hooks/rules_hook.json",
        ".claude/hooks/rules_hook.py",
        ".claude/settings.json",
        "CLAUDE.md",
    ]
    assert all(".gitignore" in message for _, message in found)


def pin_findings(tmp_path, rev):
    """Write current copies with the planted rev and return the findings."""
    shared_files.write_copies(tmp_path)
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            shared_files.TEMPLATE_REV, rev
        ),
        encoding="utf-8",
    )
    track(tmp_path)
    return shared_files.findings(tmp_path)


@pytest.mark.parametrize(
    "rev", ["main", "my-branch", "984e044b9246b289669a6134292a4be25e981f6d"]
)
def test_any_pin_passes(tmp_path, rev):
    """The rev is the repository's to choose; only the hooks must be there."""
    assert pin_findings(tmp_path, rev) == []


def test_a_config_without_the_standards_hooks_is_reported(tmp_path):
    shared_files.write_copies(tmp_path)
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
    track(tmp_path)
    ((path, message),) = shared_files.findings(tmp_path)
    assert path == ".pre-commit-config.yaml"
    assert shared_files.HOOKS_URL in message


def test_an_edited_caller_is_reported(tmp_path):
    """A caller pointed at another branch of the workflow is one finding."""
    shared_files.write_copies(tmp_path)
    caller = tmp_path / ".github" / "workflows" / "checks.yml"
    caller.write_text(
        caller.read_text(encoding="utf-8").replace("@main", "@my-branch"),
        encoding="utf-8",
    )
    track(tmp_path)
    assert [path for path, _ in shared_files.findings(tmp_path)] == [
        ".github/workflows/checks.yml"
    ]


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_templates_carry_current_copies(template):
    assert shared_files.findings(template) == []


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_templates_pin_the_same_commit(template):
    """Every template starts a new repository on the same commit."""
    assert shared_files.pre_commit_rev(template) == shared_files.TEMPLATE_REV

"""The tool entry points find the shipped settings and refuse bad usage."""

import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from standards import tools

CONFIGS = Path(__file__).parents[1] / "src" / "standards" / "configs"


def test_config_path_is_the_shipped_file():
    """The returned path reads back the same text as the file in configs."""
    path = Path(tools.config_path("ruff.toml"))
    expected = (CONFIGS / "ruff.toml").read_text(encoding="utf-8")
    assert path.read_text(encoding="utf-8") == expected


def test_unknown_config_names_itself():
    with pytest.raises(SystemExit, match="no shipped configuration named x"):
        tools.config_path("x")


@pytest.mark.parametrize("argv", [[], ["lint"]])
def test_ruff_needs_check_or_format(argv):
    with pytest.raises(SystemExit, match="usage: standards-ruff"):
        tools.run_ruff(argv)


def test_config_command_needs_one_name():
    with pytest.raises(SystemExit, match="usage: standards-config NAME"):
        tools.print_config_path(["a", "b"])


def test_markdown_missing_node_explains_installation(monkeypatch):
    """A missing Node installation produces an actionable prerequisite."""
    monkeypatch.setattr(tools.shutil, "which", lambda _name: None)
    with pytest.raises(SystemExit, match="Install Node.js 24"):
        tools.main_markdown()


def test_local_rules_hook_accepts_the_standards_repository():
    """Rule examples pass when the hook loads their recorded exceptions."""
    root = Path(__file__).parents[1]
    config = yaml.safe_load((root / ".pre-commit-config.yaml").read_text())
    hooks = config["repos"][0]["hooks"]
    entry = next(
        hook["entry"] for hook in hooks if hook["id"] == "rules-check"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "standards.rules_check",
            *shlex.split(entry)[1:],
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 blocking finding(s)" in result.stdout

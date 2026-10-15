"""The markdown-format hook runs the check's Prettier with its settings."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from standards import markdown_wrap, tools

ROOT = Path(__file__).parents[1]
CONFIGS = ROOT / "src" / "standards" / "configs"


def hook():
    """Return the markdown-format entry of .pre-commit-hooks.yaml."""
    hooks = yaml.safe_load((ROOT / ".pre-commit-hooks.yaml").read_text())
    return next(entry for entry in hooks if entry["id"] == "markdown-format")


@pytest.fixture
def command(monkeypatch):
    """Capture the formatter invocation without downloading tools."""
    calls = []
    monkeypatch.setattr(tools.shutil, "which", lambda _name: "npx")
    monkeypatch.setattr(tools.sys, "argv", ["standards-markdown", "a b.md"])

    def run(args):
        calls.append(args)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(tools.subprocess, "run", run)
    with pytest.raises(SystemExit) as result:
        tools.main_markdown()
    assert result.value.code == 0
    return calls[0]


def test_the_hook_runs_the_pinned_prettier(command):
    package = json.loads((CONFIGS / "package.json").read_text())
    version = package["dependencies"]["prettier"]
    assert hook()["entry"] == "standards-markdown"
    assert hook()["language"] == "python"
    assert f"--package=prettier@{version}" in command
    assert command[-1] == "a b.md"


def test_the_hook_uses_the_markdown_settings_of_the_check(command):
    """The hook reads the packaged configuration used by hosted CI."""
    settings = yaml.safe_load((CONFIGS / "prettierrc.yaml").read_text())
    (markdown,) = [o for o in settings["overrides"] if o["files"] == "*.md"]
    config = Path(command[command.index("--config") + 1])
    assert yaml.safe_load(config.read_text()) == settings
    assert "--no-editorconfig" in command
    assert markdown["options"]["printWidth"] == markdown_wrap.WIDTH

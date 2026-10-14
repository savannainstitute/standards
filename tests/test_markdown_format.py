"""The markdown-format hook runs the check's Prettier with its settings."""

import json
from pathlib import Path

import yaml

from standards import markdown_wrap

ROOT = Path(__file__).parents[1]
CONFIGS = ROOT / "src" / "standards" / "configs"


def hook():
    """Return the markdown-format entry of .pre-commit-hooks.yaml."""
    hooks = yaml.safe_load((ROOT / ".pre-commit-hooks.yaml").read_text())
    return next(entry for entry in hooks if entry["id"] == "markdown-format")


def test_the_hook_runs_the_pinned_prettier():
    package = json.loads((CONFIGS / "package.json").read_text())
    version = package["dependencies"]["prettier"]
    assert hook()["additional_dependencies"] == [f"prettier@{version}"]


def test_the_hook_uses_the_markdown_settings_of_the_check():
    """The hook takes flags, since it cannot read the check's settings file."""
    settings = yaml.safe_load((CONFIGS / "prettierrc.yaml").read_text())
    (markdown,) = [o for o in settings["overrides"] if o["files"] == "*.md"]
    entry = hook()["entry"]
    assert f"--print-width {markdown['options']['printWidth']}" in entry
    assert f"--prose-wrap {markdown['options']['proseWrap']}" in entry
    assert markdown["options"]["printWidth"] == markdown_wrap.WIDTH

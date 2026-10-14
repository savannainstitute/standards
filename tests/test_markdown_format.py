"""Generated Markdown is wrapped as Prettier wraps it, with one set of settings."""

import json
from pathlib import Path

import yaml

from standards import markdown_wrap

ROOT = Path(__file__).parents[1]
CONFIGS = ROOT / "src" / "standards" / "configs"


def test_a_code_span_is_never_split():
    """The span holds three spaces; it stays one word."""
    assert markdown_wrap.words("a `b c d` e") == ["a", "`b c d`", "e"]


def test_fill_breaks_before_the_word_that_passes_the_width():
    """Twenty 4-letter words and 19 spaces make 99 columns; the 21st goes to line 2."""
    text = " ".join(["word"] * 21)
    first, second = markdown_wrap.fill(text).split("\n")
    assert len(first) == 99
    assert second == "word"


def test_list_items_hang_two_spaces():
    """The prefix "- " plus 24 words of 3 letters and 23 spaces is 97; the 25th wraps."""
    text = " ".join(["abc"] * 25)
    first, second = markdown_wrap.fill(text, "- ", "  ").split("\n")
    assert len(first) == 97
    assert second == "  abc"


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

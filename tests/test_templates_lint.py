"""Each template's Python passes ruff as a repository made from it would."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from standards import tools

ROOT = Path(__file__).parents[1]
TEMPLATES = sorted(
    p
    for p in (ROOT / "templates").iterdir()
    if p.is_dir() and any(p.rglob("*.py"))
)


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
@pytest.mark.parametrize("command", [["check"], ["format", "--check"]])
def test_template_passes_ruff_on_its_own(tmp_path, template, command):
    copy = tmp_path / template.name
    shutil.copytree(template, copy)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            *command,
            "--config",
            tools.config_path("ruff.toml"),
            ".",
        ],
        cwd=copy,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

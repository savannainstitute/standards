"""The agent hook denies, reports and allows exactly the planted cases.

Every expected decision below was written by hand from the rule list before
the hook existed. Characters the typography rule refuses are built from their
code points so this file does not trip the rule it tests.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).parents[1] / "src/standards/agent/rules_hook.py"
EM_DASH = chr(0x2014)
CURLY = chr(0x201C)
EMOJI = chr(0x1F600)


def run_hook(mode, payload):
    """Run the hook as Claude Code does and return (exit code, output)."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    result = subprocess.run(
        [sys.executable, str(HOOK), mode],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    output = json.loads(result.stdout) if result.stdout.strip() else None
    return result.returncode, output


def write_payload(path, content):
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": str(path), "content": content},
    }


def decision(output):
    return output["hookSpecificOutput"]["permissionDecision"]


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("a.py", "x = 1  # fine\n"),
        ("a.py", "text = '**kept**'\n"),
        ("README.md", "The API_KEY is read when NOT_SET is absent.\n"),
        ("blob.bin", f"left {EM_DASH} right\n"),
    ],
)
def test_post_write_is_silent_on_text_typography_allows(
    tmp_path, name, content
):
    target = tmp_path / name
    target.write_text(content, encoding="utf-8")
    code, output = run_hook("post-write", write_payload(target, content))
    assert code == 0
    assert output is None


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("a.py", f"x = 1  # left {EM_DASH} right\n"),
        ("a.R", f"x <- {CURLY}a{CURLY}\n"),
        ("README.md", "This is **bold** text.\n"),
        ("README.md", "This is IMPORTANT to read.\n"),
        ("a.py", "# This is IMPORTANT to read.\nx = 1\n"),
        ("a.yaml", f"key: {EMOJI}\n"),
    ],
)
def test_post_write_reports_typography_and_never_refuses(
    tmp_path, name, content
):
    """Each planted character or word is on line 1; the write is allowed."""
    target = tmp_path / name
    target.write_text(content, encoding="utf-8")
    code, output = run_hook("post-write", write_payload(target, content))
    assert code == 0
    assert "permissionDecision" not in output["hookSpecificOutput"]
    context = output["hookSpecificOutput"]["additionalContext"]
    assert context.splitlines()[1:] == ["line 1: typography"]


def test_there_is_no_mode_that_refuses_a_write():
    result = subprocess.run(
        [sys.executable, str(HOOK), "pre-write"],
        input="{}",
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "usage" in result.stderr


PLANTED = "\n".join(
    [
        "import os",
        "",
        "# first line of a block",
        "# second line of a block",
        "# third line of a block",
        "x = 1",
        "y = 2  # updated to fix the count, as requested",
        "z = 3  # a robust default",
        "w = 4  # this is not a bug, but a feature",
        "",
    ]
)


def test_post_write_reports_each_planted_line(tmp_path):
    """Banner starts on line 3; narration 7, sales 8 and contrast 9."""
    target = tmp_path / "planted.py"
    target.write_text(PLANTED, encoding="utf-8")
    code, output = run_hook("post-write", write_payload(target, PLANTED))
    assert code == 0
    context = output["hookSpecificOutput"]["additionalContext"]
    assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    lines = sorted(context.splitlines()[1:])
    assert lines == [
        "line 3: banner",
        "line 7: narration",
        "line 8: sales-vocabulary",
        "line 9: contrast",
    ]


def test_post_write_is_silent_on_a_clean_file(tmp_path):
    target = tmp_path / "clean.py"
    target.write_text("x = 1  # the unit is meters\n", encoding="utf-8")
    code, output = run_hook("post-write", write_payload(target, ""))
    assert code == 0
    assert output is None


def shell_payload(project, command, tool="Bash"):
    return {
        "tool_name": tool,
        "cwd": str(project),
        "tool_input": {"command": command},
    }


@pytest.mark.parametrize(
    "command",
    [
        "git status",
        "rm notes.txt",
        "rm -rf build",
        "rm -rf ./build/cache && echo done",
        "rm -rf {project}/build",
    ],
)
def test_pre_shell_allows(tmp_path, command):
    command = command.format(project=tmp_path.as_posix())
    code, output = run_hook("pre-shell", shell_payload(tmp_path, command))
    assert code == 0
    assert output is None


@pytest.mark.parametrize(
    ("command", "tool"),
    [
        ("rm -rf /", "Bash"),
        ("rm -rf ~", "Bash"),
        ("rm -fr $HOME/data", "Bash"),
        ("rm -r ../elsewhere", "Bash"),
        ("cd src && rm -rf {outside}", "Bash"),
        ("Remove-Item -Recurse -Force {outside}", "PowerShell"),
        ("Remove-Item -Recurse -Force ..", "PowerShell"),
    ],
)
def test_pre_shell_denies(tmp_path, command, tool):
    project = tmp_path / "project"
    project.mkdir()
    outside = (tmp_path / "outside").as_posix()
    command = command.format(outside=outside)
    payload = shell_payload(project, command, tool)
    code, output = run_hook("pre-shell", payload)
    assert code == 0
    assert decision(output) == "deny"
    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
    assert "outside this project" in reason

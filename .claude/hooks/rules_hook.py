"""Coding agent hook: catch the organization's style rules while editing.

Usage: rules_hook.py post-write | pre-shell | stop claude|codex|gemini

The agent passes the event as JSON on standard input. post-write reads the
file Claude Code just wrote and tells it which lines the pull request check
will report for the writing rules and decision-attribution; it never
refuses a write. pre-shell
refuses a recursive delete that reaches outside the project. stop runs when
Claude Code, Codex or Gemini ends its turn: it runs pre-commit on every file
changed in the working tree when pre-commit is installed, reads those files
and, when pre-commit fails or the check would report a line, sends the agent
back once with the list. The patterns come from rules_hook.json beside this
file, which the organization's standards repository renders from the same
list its check uses.
"""

import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path

RECURSIVE_FLAG = re.compile(r"^(-[A-Za-z]*[rR][A-Za-z]*|--recursive|/s)$")
POWERSHELL_RECURSE = re.compile(r"^-r", re.I)
DELETE_COMMANDS = {"rm", "remove-item", "ri", "rmdir", "rd", "del", "erase"}
HOME_PREFIXES = ("~", "$home", "${home}", "$env:userprofile", "%userprofile%")
SEGMENT = re.compile(r"&&|\|\||[;|\n]")
DRIVE = re.compile(r"^([A-Za-z]):(/|$)")
SKIPPED_COMMENT_STARTS = ("#!", "#'", "# -*-")
# The decision word each tool's end-of-turn event reads as "keep working".
CONTINUE_DECISION = {"claude": "block", "codex": "block", "gemini": "deny"}


def load_patterns():
    """Return the patterns file that sits beside this script."""
    path = Path(__file__).with_name("rules_hook.json")
    return json.loads(path.read_text(encoding="utf-8"))


def file_kind(path, patterns):
    """Return code, markdown, config or None for a file the check skips."""
    suffix = Path(path).suffix.lower()
    for kind in ("code", "markdown", "config"):
        if suffix in patterns[f"{kind}_suffixes"]:
            return kind
    return None


def comment_of(line, marker):
    """Return the comment part of a code line, or an empty string."""
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif line.startswith(marker, i):
            return line[i:]
        i += 1
    return ""


def comment_marker(path, patterns):
    """Return the line comment marker for the file's language."""
    slash = Path(path).suffix.lower() in patterns["slash_suffixes"]
    return "//" if slash else "#"


def prose_lines(path, text, kind, patterns):
    """Yield (line number, prose) for each comment or Markdown line."""
    marker = comment_marker(path, patterns)
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if kind == "markdown":
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            elif not in_fence:
                yield n, line
        elif kind == "code":
            comment = comment_of(line, marker)
            if comment:
                yield n, comment


def has_caps_emphasis(text, patterns):
    """Whether the text carries one of the emphasis words in capitals."""
    for match in re.finditer(patterns["caps_token"], text):
        if match.group(0) not in patterns["emphasis_words"]:
            continue
        start, end = match.span()
        before = text[start - 1] if start else " "
        after = text[end] if end < len(text) else " "
        glued = (
            before in patterns["glued_before"]
            or after in patterns["glued_after"]
        )
        if not glued:
            return True
    return False


def typography_lines(path, text, kind, patterns):
    """Return the numbers of the lines the typography rule reports."""
    found = set()
    for n, line in enumerate(text.splitlines(), 1):
        if re.search(patterns["characters"], line) or re.search(
            patterns["emoji"], line
        ):
            found.add(n)
    for n, prose in prose_lines(path, text, kind, patterns):
        bold = kind == "markdown" and re.search(patterns["bold"], prose)
        if bold or has_caps_emphasis(prose, patterns):
            found.add(n)
    return found


def is_full_comment(line, marker):
    """Whether the line holds a comment and nothing else."""
    stripped = line.strip()
    return stripped.startswith(marker) and not stripped.startswith(
        SKIPPED_COMMENT_STARTS
    )


def banner_lines(path, text, patterns):
    """Return the first line of each comment block the banner rule reports."""
    marker = comment_marker(path, patterns)
    found = []
    start, length, dividers = None, 0, []
    for n, line in enumerate([*text.splitlines(), ""], 1):
        if is_full_comment(line, marker):
            start = start or n
            length += 1
            if re.match(patterns["divider"], line):
                dividers.append(n)
            continue
        found.extend([start] if length >= 3 else dividers)
        start, length, dividers = None, 0, []
    return found


def review_findings(path, text, patterns):
    """Return (line, rule id) pairs the pull request check will report."""
    kind = file_kind(path, patterns)
    if kind is None:
        return []
    found = {
        (n, "typography") for n in typography_lines(path, text, kind, patterns)
    }
    for n, prose in prose_lines(path, text, kind, patterns):
        if any(re.search(p, prose, re.I) for p in patterns["contrast"]):
            found.add((n, "contrast"))
        spelling_text = (
            ""
            if prose.lstrip().startswith(">")
            else re.sub(patterns["backtick"], "", prose)
        )
        if re.search(patterns["british"], spelling_text, re.I):
            found.add((n, "british-spelling"))
        if re.search(patterns["sales"], prose, re.I):
            found.add((n, "sales-vocabulary"))
        if kind == "code" and re.search(patterns["narration"], prose, re.I):
            found.add((n, "narration"))
        if re.search(patterns["decision_attribution"], prose):
            found.add((n, "decision-attribution"))
    if kind == "config":
        found.update(
            (n, "decision-attribution")
            for n, line in enumerate(text.splitlines(), 1)
            if re.search(patterns["decision_attribution"], line)
        )
    if kind == "code":
        found.update((n, "banner") for n in banner_lines(path, text, patterns))
    return sorted(found)


def normalize(path):
    """Return the path with forward slashes and a Git Bash style drive."""
    path = path.replace("\\", "/")
    drive = DRIVE.match(path)
    if drive:
        path = "/" + drive.group(1).lower() + "/" + path[drive.end() :]
    return posixpath.normpath(path)


def is_absolute(path):
    """Whether the path is absolute on Windows or a POSIX system."""
    return path.startswith(("/", "\\")) or bool(
        DRIVE.match(path.replace("\\", "/"))
    )


def outside_project(target, working_dir, project):
    """Whether a delete target is not strictly inside the project folder."""
    if target.lower().startswith(HOME_PREFIXES):
        return True
    if target.startswith(("$", "%")):
        return False
    if is_absolute(target):
        full = normalize(target)
    else:
        full = normalize(working_dir + "/" + target)
    return not full.startswith(normalize(project) + "/")


def recursive_delete_targets(command):
    """Yield the targets of each recursive delete in a shell command."""
    for segment in SEGMENT.split(command):
        tokens = [t.strip("\"'") for t in segment.split()]
        if not tokens:
            continue
        name = posixpath.basename(tokens[0].replace("\\", "/")).lower()
        if name not in DELETE_COMMANDS:
            continue
        flags = [t for t in tokens[1:] if t.startswith(("-", "/s", "/S"))]
        recursive = any(
            RECURSIVE_FLAG.match(f)
            or (name != "rm" and POWERSHELL_RECURSE.match(f))
            for f in flags
        )
        if recursive:
            yield from (t for t in tokens[1:] if t not in flags and t != "--")


def deny(reason):
    """Print the response that refuses the tool call."""
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(response))


def post_write(call, patterns):
    """Tell the agent which lines of the written file the check reports."""
    path = call["tool_input"]["file_path"]
    if not Path(path).is_file():
        return
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    found = review_findings(path, text, patterns)
    if not found:
        return
    lines = [
        f"The pull request check will report these in {Path(path).name}; "
        "AGENTS.md says how to fix each:"
    ]
    lines.extend(f"line {n}: {rule}" for n, rule in found)
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(response))


def pre_shell(call):
    """Refuse a recursive delete that reaches outside the project folder."""
    working_dir = call["cwd"]
    project = os.environ.get("CLAUDE_PROJECT_DIR") or working_dir
    command = call["tool_input"]["command"]
    for target in recursive_delete_targets(command):
        if outside_project(target, working_dir, project):
            deny(
                f"This command deletes {target} and everything under it, "
                "which is outside this project or is the project folder "
                "itself. Ask the person to run it themselves if it is "
                "intended."
            )
            return


def changed_files(working_dir):
    """Return the repository root and its changed or new files, or None."""
    top = subprocess.run(
        ["git", "-C", working_dir, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if top.returncode != 0:
        return None
    root = top.stdout.strip()
    status = subprocess.run(
        ["git", "-C", root, "status", "--porcelain", "-z", "-uall"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    entries = iter(status.stdout.split("\0"))
    paths = []
    for entry in entries:
        if not entry:
            continue
        if entry[0] in "RC":
            next(entries, None)
        path = entry[3:]
        if (Path(root) / path).is_file():
            paths.append(path)
    return root, sorted(paths)


def pre_commit_report(root, paths):
    """Run pre-commit on the changed files and return its report if it fails.

    Runs only when pre-commit is installed and the repository configures it;
    otherwise, and when it passes, the report is empty.
    """
    program = shutil.which("pre-commit")
    configured = (Path(root) / ".pre-commit-config.yaml").is_file()
    if not paths or program is None or not configured:
        return ""
    result = subprocess.run(
        [program, "run", "--color", "never", "--files", *paths],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        return ""
    return (result.stdout + result.stderr).strip()


def stop(call, tool, patterns):
    """Send the agent back once when a changed file has a finding."""
    if call.get("stop_hook_active"):
        return
    changed = changed_files(call.get("cwd") or os.getcwd())
    if changed is None:
        return
    root, paths = changed
    report = pre_commit_report(root, paths)
    lines = []
    for path in paths:
        text = (Path(root) / path).read_text(
            encoding="utf-8", errors="replace"
        )
        lines.extend(
            f"{path} line {n}: {rule}"
            for n, rule in review_findings(path, text, patterns)
        )
    parts = []
    if lines:
        lines.insert(
            0,
            "Before you finish, the pull request check will report these "
            "lines in the files changed here. Fix each as AGENTS.md says, or "
            "say in your reply why a line stays:",
        )
        parts.append("\n".join(lines))
    if report:
        parts.append(
            "pre-commit failed on the files changed here, or fixed some of "
            "them itself; read what it changed and fix the rest. Its "
            "report:\n" + report
        )
    if not parts:
        return
    reason = "\n\n".join(parts)
    print(json.dumps({"decision": CONTINUE_DECISION[tool], "reason": reason}))


def main(argv=None):
    """Read the event from standard input and run the named mode."""
    argv = sys.argv[1:] if argv is None else argv
    valid = argv in (["post-write"], ["pre-shell"]) or (
        len(argv) == 2 and argv[0] == "stop" and argv[1] in CONTINUE_DECISION
    )
    if not valid:
        raise SystemExit(
            "usage: rules_hook.py post-write|pre-shell"
            "|stop claude|codex|gemini"
        )
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    call = json.loads(raw)
    if argv[0] == "pre-shell":
        pre_shell(call)
    elif argv[0] == "stop":
        stop(call, argv[1], load_patterns())
    else:
        post_write(call, load_patterns())
    return 0


if __name__ == "__main__":
    sys.exit(main())

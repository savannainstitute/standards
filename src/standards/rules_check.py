"""Check a repository against the rule list in rules.py.

Tree rules read every tracked file. Diff rules read the pull request's
changes between a base and a head commit. Text rules read the commit
messages in that range and the pull request text. Each finding names the
rule, the file and the line; a blocking finding makes the exit code 1.

Usage:
    rules-check [--repo-dir DIR] [--base SHA] [--head SHA] [--pr-body FILE]
               [--repo OWNER/NAME] [--standards-root DIR]

Without --base only the tree rules run, which is how the pre-commit hook
uses it.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

from standards import rules, shared_files

CODE_SUFFIXES = {
    ".py",
    ".r",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".mjs",
    ".cjs",
    ".sh",
    ".bash",
    ".kt",
    ".swift",
    ".dockerfile",
}
MARKDOWN_SUFFIXES = {".md", ".rmd", ".qmd"}
CONFIG_SUFFIXES = {
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".jsonc",
    ".ini",
    ".cfg",
    ".txt",
}
SLASH_COMMENT_SUFFIXES = {
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".mjs",
    ".cjs",
    ".kt",
    ".swift",
}
MANIFESTS = (
    "pyproject.toml",
    "environment.yml",
    "DESCRIPTION",
    "package.json",
)
# Larger files are data or generated; GitHub's diff view stops at this size.
MAX_BYTES = 1_000_000
# renv::init writes this script and renv rewrites it; nobody edits it.
TOOL_WRITTEN = re.compile(r"(^|/)renv/activate\.R$")

CONTRAST = [
    re.compile(r"\bnot\b[^.;\n]{1,60},\s*but\b", re.I),
    re.compile(r"\bisn'?t\b[^.;\n]{1,60},\s*it'?s\b", re.I),
    re.compile(r"\b(it'?s|this is)\b[^.;\n]{1,60},\s*(never|not)\b", re.I),
]
NARRATION = re.compile(
    r"\b(now we|updated to|as requested|per (the|your) (request|feedback)"
    r"|changed (this|it) to|this (now|fix) )\b",
    re.I,
)
PERSON = r"[A-Z][a-z]+\b"
ISO_DATE = r"\d{4}-\d{2}-\d{2}"
DECIDED = r"(?i:decided|approved|agreed|confirmed|requested|chose|chosen)"
DECISION_ATTRIBUTION = re.compile(
    rf"\(\s*{PERSON}(\s+{PERSON})?,\s*{ISO_DATE}\s*\)"
    rf"|\b{DECIDED}\b(\s+\w+){{0,3}}?\s+(by\s+{PERSON}|on\s+{ISO_DATE})"
    rf"|\b{PERSON}\s+(asked|wants|prefers|decided|approved)\b"
    rf"|\bper\s+{PERSON}('s\b|\s+{ISO_DATE})"
)
DIVIDER = re.compile(r"^\s*(#|//)\s*[-=*_]{5,}")
HISTORY = re.compile(
    r"\b20\d\d-\d\d-\d\d\b|\boriginally\b|\bhistorically\b"
    r"|\bbecause the previous\b",
    re.I,
)
CHAT_CODE = [
    re.compile(r"^\s*```"),
    re.compile(r"\braise\s+NotImplementedError\b"),
    re.compile(r"stop\(\s*[\"']not implemented", re.I),
]
CHAT_PROSE = [
    re.compile(r"here is the (updated|full|complete)", re.I),
    re.compile(r"rest of (the )?(code|file) (unchanged|remains)", re.I),
    re.compile(r"\.\.\. ?(existing|rest)\b", re.I),
    re.compile(r"TODO: implement", re.I),
]
EM_DASH = re.compile(chr(0x2014))
EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\u2b50\u2b55]")
BOLD = re.compile(r"(\*\*|__)[^*_\n]+\1")
CAPS_TOKEN = re.compile(r"[A-Z][A-Z0-9]{2,}")
EMPHASIS_WORDS = {
    "NOT",
    "NEVER",
    "ALWAYS",
    "MUST",
    "SHOULD",
    "DO",
    "DONT",
    "IMPORTANT",
    "CRITICAL",
    "WARNING",
    "NOTE",
    "REQUIRED",
    "ONLY",
    "ALL",
    "ANY",
    "EVERY",
}
GLUED_BEFORE = "._-\"'"
GLUED_AFTER = "._-(\"'"
SALES = re.compile(
    r"\b(robust|comprehensive|seamless(ly)?|production-ready)\b", re.I
)
SCRATCH_NAME = re.compile(
    r"^scratch(pad)?([_-].*)?\.(md|txt|py|r)$"
    r"|^(plans?|summary|time_?log|sessions?|notes?|todo)([_-].*)?\.(md|txt)$"
    r"|[_-](plan|notes|summary|time_?log|scratchpad)\.(md|txt)$",
    re.I,
)
COPY_SUFFIX = re.compile(
    r"(_v\d+|_new|-new|_final|_backup|_old|_copy|\d{8}|\d{4}-\d{2}-\d{2})"
    r"\.[A-Za-z0-9]+$",
    re.I,
)
DATA_DIR = re.compile(r"(^|/)(data|raw_data)/")
# Someone else's software, which an environment file names instead (B8).
INSTALLER_SUFFIXES = {".whl", ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"}
# The kinds B8 sends through LFS: images, rasters, point clouds, video, R
# data, models, archives, PDFs, spreadsheets; configs/gitattributes lists them.
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".heic", ".tif",
    ".tiff", ".las", ".laz", ".ply", ".pcd", ".mp4", ".mov", ".avi",
    ".rds", ".rda", ".rdata", ".pt", ".pth", ".h5", ".hdf5", ".onnx",
    ".pkl", ".joblib", ".npy", ".npz", ".zip", ".tar", ".gz", ".tgz",
    ".7z", ".pdf", ".gpkg", ".shp", ".dbf", ".parquet", ".feather",
    ".xlsx", ".docx", ".pptx",
}  # fmt: skip
LFS_POINTER = "version https://git-lfs.github.com/spec/v1"
DATA_README = "data/README.md"
MACHINE_COMPONENTS = {
    ".DS_Store",
    "Thumbs.db",
    ".Rhistory",
    ".RData",
    "__pycache__",
    "node_modules",
    ".ipynb_checkpoints",
    "dist",
    "build",
    ".vscode",
}
SILENT_DEFAULT = re.compile(
    r"\.get\([^,()]+,\s*(None|\"\"|''|0|\[\]|\{\})\)|%\|\|%|ifelse\(is\.na"
    r"|\?\?\s*(null|\"\"|''|0|\[\])"
)
MACHINE_PATH = re.compile(
    r"[A-Za-z]:[\\/]+Users[\\/]+|/Users/[A-Za-z0-9_.-]+/"
    r"|/home/[a-z][a-z0-9_-]*/|Dropbox[\\/]|[\\/]Dropbox\b"
)
SILENCERS = re.compile(
    r"(#\s*noqa\b|#\s*type:\s*ignore\b|#\s*nolint\b|eslint-disable[a-z-]*"
    r"|shellcheck disable|pragma:\s*no cover"
    r"|@pytest\.mark\.(skipif|skip|xfail)\b|pytest\.(skip|xfail)\("
    r"|^\s*skip\(|\b(it|test|describe)\.(skip|skipIf|todo)\(|\bxit\("
    r"|#\s*hadolint ignore)",
    re.I,
)
RULE_TOKEN = re.compile(r"^[\s:\[\(=]*[A-Za-z][A-Za-z0-9_/,-]*\d*[\]\s,]*")
JS_SKIP = re.compile(r"\b(it|test|describe)\.(skip|skipIf|todo)\(|\bxit\(")
# A Dockerfile has no suffix; it is read as code with # comments.
DOCKERFILE = re.compile(r"^(Dockerfile|Containerfile)(\..*)?$|\.dockerfile$")
WORD = re.compile(r"[A-Za-z]{2,}")
CONSTANT = re.compile(r"^\s*[A-Z][A-Z0-9_]{2,}\s*(=|<-)\s*-?\d")
SWALLOW = re.compile(
    r"error\s*=\s*function\s*\([^)]*\)\s*(NULL|NA|\{\s*\})"
    r"|try\(.*silent\s*=\s*TRUE"
)
ALWAYS_TRUE = re.compile(
    r"assert\s+True\b|expect_true\(\s*TRUE\s*\)"
    r"|expect\(\s*true\s*\)\.toBe\(\s*true\s*\)|assertTrue\(\s*True\s*\)"
)
DOI = re.compile(r"\b10\.\d{4,9}/\S+")
FILE_TEST = re.compile(
    r"exists\(|isfile\(|is_file\(|file\.exists\(|existsSync\("
)
SYNTHETIC = re.compile(
    r"\b(sample|example|synthetic|dummy|rnorm|runif|np\.random|random\.)",
    re.I,
)
ROW_DROP = re.compile(r"\b(dropna|fillna|na\.omit|drop_na)\(|filter\(!is\.na")
BACKTICK = re.compile(r"`([^`\n]+)`")
PATH_EXTENSIONS = {
    "py",
    "r",
    "rmd",
    "qmd",
    "md",
    "txt",
    "yml",
    "yaml",
    "toml",
    "json",
    "jsonc",
    "csv",
    "tsv",
    "ipynb",
    "sh",
    "js",
    "ts",
    "tsx",
    "jsx",
    "mjs",
    "cjs",
    "html",
    "css",
    "cfg",
    "ini",
    "lock",
    "xml",
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "tif",
    "tiff",
    "gpkg",
    "shp",
    "parquet",
    "rda",
    "rds",
    "rproj",
    "sql",
    "env",
    "gitignore",
}
SECRET = re.compile(
    r"\b(password|passwd|pwd|secret|token|api_key|apikey|access_key"
    r"|private_key|client_secret)\w*\s*(=|:=|<-|:)\s*[\"']([^\"'\n]{6,})[\"']",
    re.I,
)
SECRET_NAME_EXEMPT = re.compile(
    r"file|path|name|_id|url|header|field|column|prompt|label|env|tool", re.I
)
PLACEHOLDER = re.compile(
    r"^<.*>$|\$\{|\{\{|^x+$|your_|changeme|example|placeholder|/|\s"
    r"|\.[a-z]{1,5}$",
    re.I,
)
TEST_PATH = re.compile(r"(^|/)tests?(/|_)|_test\.|\.test\.|test_")
SOURCE_DIRS = ("src/", "R/", "packages/")
DEFINITION = {
    ".py": re.compile(r"^(async\s+def|def|class)\s", re.M),
    ".r": re.compile(r"^[A-Za-z._][\w.]*\s*(<-|=)\s*function\s*\(", re.M),
    **dict.fromkeys(
        (".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx"),
        re.compile(
            r"^\s*(export\s+)?(default\s+)?(async\s+)?(function|class)\b"
            r"|^\s*(export\s+)?(const|let)\s+\w+\s*=\s*(async\s*)?"
            r"(\([^)]*\)|\w+)\s*(:\s*[^=]+)?=>",
            re.M,
        ),
    ),
}
TEST_NAME = re.compile(
    r"^test_(\w+)\.py$|^(\w+)_test\.py$|^test[-_]([\w.-]+)\.[Rr]$"
    r"|^([\w.-]+)\.(?:test|spec)\.[cm]?[jt]sx?$"
)
UNTESTED_EXEMPT_DIR = re.compile(r"(^|/)(docs|data|raw_data|notebooks)/")
CONFIG_NAME = re.compile(r"\.config\.[cm]?[jt]s$|\.d\.ts$")
# Files a language reserves for package setup and test fixtures.
CONVENTION_FILES = {"__init__.py", "__main__.py", "conftest.py"}
# The root documents each project layout names besides README.md.
ROOT_DOCUMENTS = {
    "AGENTS.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "NEWS.md",
    "LICENSE.md",
    "HOSTING.md",
}
REMOVED_TEST = re.compile(r"^\s*(def test_|test_that\(|(it|test)\()")
ATTRIBUTION = re.compile(
    r"Co-authored-by:.*(claude|anthropic)|Generated (with|by) \[?Claude"
    r"|noreply@anthropic\.com",
    re.I,
)


@dataclass(frozen=True)
class Finding:
    """One problem: rule id, file or text, line (0 for whole-file), message."""

    rule: str
    path: str
    line: int
    message: str

    @property
    def blocks(self):
        """Whether this finding fails the check."""
        return rules.BY_ID[self.rule].blocks


class Report:
    """Collects findings, drops duplicates and honors the repo's exemptions."""

    def __init__(self, exempt=frozenset()):
        """Start empty; exempt holds (path, rule id) pairs never reported."""
        self.findings = []
        self._seen = set()
        self._exempt = exempt

    def add(self, rule, path, line, detail=""):
        """Record one finding unless it repeats or the path is exempt."""
        key = (rule, path, line)
        if key in self._seen or (path, rule) in self._exempt:
            return
        self._seen.add(key)
        message = detail if detail else rules.BY_ID[rule].fix
        self.findings.append(Finding(rule, path, line, message))


def git(repo_dir, *args):
    """Run git in the repo and return its standard output."""
    return subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout


def tracked_files(repo_dir):
    """Return every path git tracks except tool-written ones, from the root."""
    out = git(repo_dir, "ls-files", "-z")
    return [p for p in out.split("\0") if p and not TOOL_WRITTEN.search(p)]


def read_text(repo_dir, path):
    """Return the file's text, or None for a binary or oversized file."""
    full = Path(repo_dir) / path
    if not full.is_file() or full.stat().st_size > MAX_BYTES:
        return None
    try:
        return full.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def comment_start(line, marker):
    """Index where a comment starts, ignoring quoted markers; -1 if none."""
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
            return i
        i += 1
    return -1


def python_docstring_row(line, state):
    """Classify one Python line as docstring or not; returns (row, state)."""
    quotes = line.count('"""') + line.count("'''")
    if state:
        return (line, True), quotes % 2 == 0
    starts = line.lstrip().startswith(('"""', "'''", 'r"""', "r'''"))
    if quotes == 1 and starts:
        return (line, True), True
    if quotes >= 2 and starts:
        return (line, True), False
    return None, False


def code_lines(text, suffix):
    """Split a code file into (lineno, code, comment, in_docstring) rows."""
    marker = "//" if suffix in SLASH_COMMENT_SUFFIXES else "#"
    rows = []
    in_docstring = False
    in_block = False
    for n, line in enumerate(text.splitlines(), 1):
        if suffix == ".py":
            row, in_docstring = python_docstring_row(line, in_docstring)
            if row:
                rows.append((n, "", row[0], True))
                continue
        if marker == "//":
            if in_block:
                end = line.find("*/")
                if end == -1:
                    rows.append((n, "", line, True))
                    continue
                rows.append((n, line[end + 2 :], line[:end], True))
                in_block = False
                continue
            start = line.find("/*")
            if start != -1 and "*/" not in line[start:]:
                rows.append((n, line[:start], line[start:], True))
                in_block = True
                continue
            if start != -1:
                end = line.find("*/", start)
                code = line[:start] + line[end + 2 :]
                rows.append((n, code, line[start:end], False))
                continue
        at = comment_start(line, marker)
        if at == -1:
            rows.append((n, line, "", False))
        else:
            rows.append((n, line[:at], line[at:], False))
    return rows


def is_full_comment(code, comment, line):
    """Whether the line is a comment and nothing else, shebangs excepted."""
    stripped = line.strip()
    return (
        bool(comment)
        and not code.strip()
        and not stripped.startswith(("#!", "#'", "# -*-"))
    )


def check_prose_line(report, path, n, text, in_code_comment, with_caps):
    """Apply the prose rules to one line of comment, docstring or Markdown."""
    for pattern in CONTRAST:
        if pattern.search(text):
            report.add("contrast", path, n)
    if SALES.search(text):
        report.add("sales-vocabulary", path, n)
    if DECISION_ATTRIBUTION.search(text):
        report.add("decision-attribution", path, n)
    if in_code_comment and NARRATION.search(text):
        report.add("narration", path, n)
    if with_caps and caps_emphasis(text):
        report.add(
            "typography", path, n, "All-caps emphasis; use a plain word."
        )


def caps_emphasis(text):
    """Whether the text carries an all-caps emphasis word."""
    for match in CAPS_TOKEN.finditer(text):
        if match.group(0) not in EMPHASIS_WORDS:
            continue
        start, end = match.span()
        before = text[start - 1] if start else " "
        after = text[end] if end < len(text) else " "
        if before in GLUED_BEFORE or after in GLUED_AFTER:
            continue
        return True
    return False


def check_typography_line(report, path, n, line):
    """Report an em dash or emoji on the line."""
    if EM_DASH.search(line):
        report.add("typography", path, n, "Em dash; use a comma or a period.")
    if EMOJI.search(line):
        report.add("typography", path, n, "Emoji; remove it.")


def reason_after(line, match):
    """Whether a silencing marker is followed by two or more reason words."""
    rest = line[match.end() :]
    marker = match.group(0).lstrip("#").strip().lower()
    tools = ("noqa", "type", "nolint", "eslint", "shellcheck", "hadolint")
    if marker.startswith(tools):
        rest = RULE_TOKEN.sub("", rest, count=1)
    elif JS_SKIP.match(match.group(0)):
        # The test's name is not a reason; a comment after the call is.
        rest = rest.partition("//")[2]
    return len(WORD.findall(rest)) >= 2


def code_suffix(path):
    """Return the suffix the code rules read a path under; Dockerfiles count."""
    name = PurePosixPath(path).name
    if DOCKERFILE.match(name):
        return ".dockerfile"
    return PurePosixPath(path).suffix.lower()


def check_code_line(report, path, n, lines, code, comment, in_doc, allowlist):
    """Apply every single-line code rule to one row of a code file."""
    line = lines[n - 1]
    if comment or in_doc:
        prose = comment if comment else line
        check_prose_line(report, path, n, prose, bool(comment), True)
        if HISTORY.search(prose):
            report.add("docstring-history", path, n)
        for pattern in CHAT_PROSE:
            if pattern.search(prose):
                report.add("chat-residue", path, n)
    for pattern in CHAT_CODE:
        if pattern.search(line):
            report.add("chat-residue", path, n)
    if MACHINE_PATH.search(line):
        report.add("machine-path", path, n)
    if not in_doc and SILENT_DEFAULT.search(code):
        report.add("silent-default", path, n)
    silencer = SILENCERS.search(line)
    if silencer and not reason_after(line, silencer):
        report.add("silenced-check", path, n)
    if CONSTANT.match(code) and not comment:
        previous = lines[n - 2] if n >= 2 else ""
        if not previous.strip().startswith(("#", "//")):
            report.add("unsourced-constant", path, n)
    if path.lower().endswith(".r") and SWALLOW.search(code):
        report.add("swallowed-error", path, n)
    if TEST_PATH.search(path) and ALWAYS_TRUE.search(code):
        report.add("always-true-test", path, n)
    following = lines[n] if n < len(lines) else ""
    if DOI.search(line) and "http" not in line and "http" not in following:
        report.add("unverified-citation", path, n)
    if FILE_TEST.search(code) and (
        SYNTHETIC.search(code) or SYNTHETIC.search(following)
    ):
        report.add("synthetic-fallback", path, n)
    if ROW_DROP.search(code) and not comment:
        report.add("silent-row-drop", path, n)
    secret = SECRET.search(code)
    if (
        secret
        and not SECRET_NAME_EXEMPT.search(secret.group(1))
        and not PLACEHOLDER.search(secret.group(3))
        and not (
            "public fixture" in line.lower() and secret.group(3) in allowlist
        )
    ):
        report.add("secret-literal", path, n)


def check_code_file(report, path, text, suffix, allowlist):
    """Apply the code rules, including the banner rule, to one code file."""
    lines = text.splitlines()
    block_start = None
    block_len = 0
    dividers = []

    def close_block():
        if block_len >= 3:
            report.add("banner", path, block_start)
        else:
            for divider in dividers:
                report.add("banner", path, divider)

    for n, code, comment, in_doc in code_lines(text, suffix):
        line = lines[n - 1]
        check_typography_line(report, path, n, line)
        if is_full_comment(code, comment, line) and not in_doc:
            block_start = block_start or n
            block_len += 1
            if DIVIDER.match(line):
                dividers.append(n)
        else:
            close_block()
            block_start, block_len, dividers = None, 0, []
        check_code_line(
            report, path, n, lines, code, comment, in_doc, allowlist
        )
    close_block()


def check_markdown_file(report, repo_dir, path, text):
    """Apply the prose rules to a Markdown file, skipping fenced code."""
    lines = text.splitlines()
    in_fence = False
    for n, line in enumerate(lines, 1):
        check_typography_line(report, path, n, line)
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        check_prose_line(report, path, n, line, False, True)
        for pattern in CHAT_PROSE:
            if pattern.search(line):
                report.add("chat-residue", path, n)
        if BOLD.search(BACKTICK.sub("", line)):
            report.add(
                "typography", path, n, "Bold in Markdown; use plain text."
            )
        if MACHINE_PATH.search(line):
            report.add("machine-path", path, n)
        following = lines[n] if n < len(lines) else ""
        if DOI.search(line) and "http" not in line and "http" not in following:
            report.add("unverified-citation", path, n)
    name = PurePosixPath(path).name
    if name == "README.md" or path.startswith("docs/"):
        check_readme_paths(report, repo_dir, path, lines)


def looks_like_path(token):
    """Whether a backticked token names a file or folder rather than a word."""
    if (
        " " in token
        or any(c in token for c in "<>{}*()=|$~@:")
        or token.startswith(("-", "http"))
    ):
        return False
    if token.endswith("/"):
        return len(token) > 1
    suffix = token.rsplit(".", 1)[-1].lower() if "." in token else ""
    return suffix in PATH_EXTENSIONS


def check_readme_paths(report, repo_dir, path, lines):
    """Report every backticked path in the file that does not exist."""
    here = Path(repo_dir) / PurePosixPath(path).parent
    for n, line in enumerate(lines, 1):
        for token in BACKTICK.findall(line):
            token = token.strip()
            if token.startswith("./"):
                token = token[2:]
            if not looks_like_path(token):
                continue
            if (Path(repo_dir) / token).exists() or (here / token).exists():
                continue
            report.add(
                "readme-path",
                path,
                n,
                f"`{token}` does not exist in the repo.",
            )


def check_config_file(report, path, text):
    """Apply the typography and attribution rules to a configuration file."""
    for n, line in enumerate(text.splitlines(), 1):
        check_typography_line(report, path, n, line)
        if DECISION_ATTRIBUTION.search(line):
            report.add("decision-attribution", path, n)


def check_notebook(report, repo_dir, path):
    """Report a notebook whose code cells carry outputs."""
    try:
        notebook = json.loads(
            (Path(repo_dir) / path).read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    for cell in notebook.get("cells") or []:
        if cell.get("cell_type") == "code" and (
            cell.get("outputs") or cell.get("execution_count")
        ):
            report.add("notebook-output", path, 0)
            return


def check_path(report, path):
    """Apply the three path rules to one tracked path."""
    parts = PurePosixPath(path).parts
    name = parts[-1]
    if SCRATCH_NAME.search(name):
        report.add("scratch-file", path, 0)
    if COPY_SUFFIX.search(name) and not DATA_DIR.search(path):
        report.add("copy-suffix", path, 0)
    if any(
        p in MACHINE_COMPONENTS
        or p.endswith((".pyc", ".egg-info", ".Rproj.user"))
        for p in parts
    ):
        report.add("machine-file", path, 0)
    if PurePosixPath(name).suffix.lower() in INSTALLER_SUFFIXES:
        report.add("installer-committed", path, 0)


def check_data_listed(report, repo_dir, paths):
    """Warn on each file under data/ that data/README.md does not name."""
    data_files = [
        p
        for p in paths
        if p.startswith("data/")
        and p != DATA_README
        and PurePosixPath(p).name != ".gitattributes"
    ]
    if not data_files:
        return
    readme = read_text(repo_dir, DATA_README) or ""
    for path in data_files:
        relative = path[len("data/") :]
        if relative in readme or PurePosixPath(path).name in readme:
            continue
        report.add(
            "data-unlisted",
            path,
            0,
            f"{DATA_README} does not name {relative}.",
        )


def lfs_filtered(repo_dir, path):
    """Whether .gitattributes sends the path through the LFS filter."""
    out = git(repo_dir, "check-attr", "filter", "--", path)
    return out.strip().endswith(": filter: lfs")


def binary_outside_lfs(repo_dir, head, path):
    """Whether an added binary file is committed as content, not a pointer."""
    if PurePosixPath(path).suffix.lower() not in BINARY_SUFFIXES:
        return False
    if not lfs_filtered(repo_dir, path):
        return True
    return not head_file(repo_dir, head, path).startswith(LFS_POINTER)


def override_file(standards_root, repo_name, name):
    """Path of one file under overrides/<repo>/ in the standards checkout."""
    if not standards_root or not repo_name:
        return None
    short = repo_name.split("/")[-1]
    file = Path(standards_root) / "overrides" / short / name
    return file if file.is_file() else None


def load_allowlist(standards_root, repo_name):
    """Return the public fixture literals listed for the repo."""
    file = override_file(standards_root, repo_name, "public_fixtures.yaml")
    if file is None:
        return set()
    data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
    rows = data.get("public_fixtures") or []
    return {
        row["value"]
        for row in rows
        if str(row.get("published_at") or "").startswith("http")
    }


def load_exempt(standards_root, repo_name):
    """Return the (path, rule id) pairs the repo's exempt.yaml lists."""
    file = override_file(standards_root, repo_name, "exempt.yaml")
    if file is None:
        return frozenset()
    data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
    pairs = set()
    for row in data.get("exempt") or []:
        if not str(row.get("reason") or "").strip():
            raise SystemExit(f"{file}: every exempt entry needs a reason")
        for rule in row["rules"]:
            if rule not in rules.BY_ID:
                raise SystemExit(f"{file}: unknown rule {rule}")
            pairs.add((row["path"], rule))
    return frozenset(pairs)


def defines_code(path, text):
    """Whether a code file defines a function or a class at its top level."""
    suffix = PurePosixPath(path).suffix.lower()
    pattern = DEFINITION.get(suffix)
    return bool(pattern and pattern.search(text))


def expected_test(path):
    """Return the test file the layouts name for a source file."""
    pure = PurePosixPath(path)
    stem, suffix = pure.stem, pure.suffix
    if suffix.lower() == ".py":
        return f"tests/test_{stem}.py"
    if suffix.lower() == ".r":
        return f"tests/testthat/test-{stem}.R"
    return f"tests/{stem}.test{suffix}"


def test_stems(paths):
    """Return the source stems the repository's test files are named for."""
    stems = set()
    for path in paths:
        name = PurePosixPath(path).name
        match = TEST_NAME.match(name)
        if match and TEST_PATH.search(path):
            stems.add(next(g for g in match.groups() if g))
    return stems


def is_test_covered(stem, stems):
    """Whether a test file is named for the stem or for a part of it."""
    return any(s == stem or s.startswith(stem + "_") for s in stems)


def untested_code(repo_dir, paths):
    """Return (path, expected test file) for each code file with no test."""
    code = [
        p
        for p in paths
        if PurePosixPath(p).suffix.lower() in DEFINITION
        and not any(part.startswith(".") for part in PurePosixPath(p).parts)
        and not UNTESTED_EXEMPT_DIR.search(p)
        and not TEST_PATH.search(p)
        and not CONFIG_NAME.search(PurePosixPath(p).name)
    ]
    stems = test_stems(paths)
    if code and not stems:
        return [("", "tests/")]
    found = []
    for path in code:
        if PurePosixPath(path).name in CONVENTION_FILES:
            continue
        text = read_text(repo_dir, path)
        if text is None or not defines_code(path, text):
            continue
        if not is_test_covered(PurePosixPath(path).stem, stems):
            found.append((path, expected_test(path)))
    return found


def check_tree(report, repo_dir, allowlist):
    """Apply the tree rules to every tracked file."""
    paths = tracked_files(repo_dir)
    for path, test in untested_code(repo_dir, paths):
        if path:
            message = f"Add {test}, testing what this file defines."
        else:
            message = (
                "The repository has code and no tests; add a tests folder."
            )
        report.add("untested-code", path or "tests/", 0, message)
    check_data_listed(report, repo_dir, paths)
    for path in paths:
        check_path(report, path)
        suffix = code_suffix(path)
        if suffix == ".ipynb":
            check_notebook(report, repo_dir, path)
            continue
        if suffix not in CODE_SUFFIXES | MARKDOWN_SUFFIXES | CONFIG_SUFFIXES:
            continue
        text = read_text(repo_dir, path)
        if text is None:
            continue
        if suffix in CODE_SUFFIXES:
            check_code_file(report, path, text, suffix, allowlist)
        elif suffix in MARKDOWN_SUFFIXES:
            check_markdown_file(report, repo_dir, path, text)
        else:
            check_config_file(report, path, text)


def parse_diff(repo_dir, base, head):
    """Return {path: {status, added [(line, text)], removed [text]}}."""
    changes = {}
    for row in git(repo_dir, "diff", "--name-status", base, head).splitlines():
        status, _, path = row.partition("\t")
        if status.startswith("R"):
            status, path = "A", path.split("\t")[-1]
        changes[path] = {"status": status[0], "added": [], "removed": []}
    current = None
    new_line = 0
    diff = git(repo_dir, "diff", "--no-color", "-U0", base, head)
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[4:]
            current = current[2:] if current.startswith("b/") else None
        elif line.startswith("@@"):
            hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
            new_line = int(hunk.group(1))
        elif current and line.startswith("+"):
            change = changes.setdefault(
                current, {"status": "M", "added": [], "removed": []}
            )
            change["added"].append((new_line, line[1:]))
            new_line += 1
        elif current and line.startswith("-"):
            change = changes.setdefault(
                current, {"status": "M", "added": [], "removed": []}
            )
            change["removed"].append(line[1:])
    return changes


def body_section(body, heading):
    """Text of the pull request body from a heading line to the end."""
    match = re.search(rf"^#*\s*{re.escape(heading)}\b.*$", body, re.M | re.I)
    return body[match.start() :] if match else ""


DEPENDENCY_SHAPES = {
    "pyproject.toml": re.compile(r'\s*"([A-Za-z0-9][A-Za-z0-9_.-]*)'),
    "environment.yml": re.compile(r"\s*-\s*([A-Za-z0-9][A-Za-z0-9_.-]*)"),
    "DESCRIPTION": re.compile(r"\s+([A-Za-z][A-Za-z0-9.]+)"),
    "package.json": re.compile(r'\s*"(@?[A-Za-z0-9_./-]+)":\s*"[\^~]?\d'),
    "requirements": re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)"),
}


NPM_SECTIONS = (
    "dependencies",
    "devDependencies",
    "peerDependencies",
    "optionalDependencies",
)
DESCRIPTION_FIELD = re.compile(r"^([A-Za-z@/0-9.]+):")
DESCRIPTION_SECTIONS = {"Depends", "Imports", "Suggests", "LinkingTo"}


def is_manifest(path):
    """Whether the path is a dependency manifest the check reads."""
    name = PurePosixPath(path).name
    return name in MANIFESTS or (
        name.startswith("requirements") and name.endswith(".txt")
    )


def conda_dependencies(head_text):
    """Package names under the dependencies key of a conda environment file."""
    try:
        data = yaml.safe_load(head_text) or {}
    except yaml.YAMLError:
        return set()
    names = set()
    for entry in data.get("dependencies") or []:
        if isinstance(entry, str):
            names.add(re.split(r"[=<>!\s]", entry, maxsplit=1)[0])
    return names


def npm_dependencies(head_text):
    """Package names under the dependency sections of a package.json."""
    try:
        data = json.loads(head_text)
    except json.JSONDecodeError:
        return set()
    names = set()
    for section in NPM_SECTIONS:
        names.update(data.get(section) or {})
    return names


def description_dependencies(head_text):
    """Package names under the dependency fields of an R DESCRIPTION file."""
    names = set()
    in_dependency_field = False
    for line in head_text.splitlines():
        field = DESCRIPTION_FIELD.match(line)
        if field:
            in_dependency_field = field.group(1) in DESCRIPTION_SECTIONS
            line = line[field.end() :]
        if in_dependency_field:
            names.update(re.findall(r"[A-Za-z][A-Za-z0-9.]+(?![^(]*\))", line))
    return names


DECLARED = {
    "environment.yml": conda_dependencies,
    "package.json": npm_dependencies,
    "DESCRIPTION": description_dependencies,
}


def dependency_names(path, added, head_text):
    """Return (line, package) for each added line declaring a dependency."""
    name = PurePosixPath(path).name
    key = "requirements" if name.startswith("requirements") else name
    shape = DEPENDENCY_SHAPES[key]
    declared = DECLARED[key](head_text) if key in DECLARED else None
    found = []
    for n, text in added:
        if key == "requirements" and text.lstrip().startswith(("#", "-")):
            continue
        if key == "environment.yml" and text.rstrip().endswith(":"):
            continue
        match = shape.match(text)
        if not match:
            continue
        if declared is not None and match.group(1) not in declared:
            continue
        found.append((n, match.group(1)))
    return found


def head_file(repo_dir, head, path):
    """Text of the file at the head commit, or '' when it is not there."""
    try:
        return git(repo_dir, "show", f"{head}:{path}")
    except subprocess.CalledProcessError:
        return ""


def check_diff(report, repo_dir, base, head, body):
    """Apply the pull request rules to the changes between base and head."""
    changes = parse_diff(repo_dir, base, head)
    docs_added = body_section(body, "Docs added").lower()
    dependencies = body_section(body, "Dependencies").lower()
    tests_removed = body_section(body, "Tests removed or skipped")
    source_changed = []
    test_lines_added = False
    for path, change in changes.items():
        if (
            change["status"] == "A"
            and path.endswith(".md")
            and PurePosixPath(path).name != "README.md"
            and path not in ROOT_DOCUMENTS
            and not path.startswith("docs/")
            and path.lower() not in docs_added
        ):
            report.add("stray-markdown", path, 0)
        added_binary = change["status"] == "A" and binary_outside_lfs(
            repo_dir, head, path
        )
        if added_binary:
            report.add("binary-outside-lfs", path, 0)
        if is_manifest(path):
            head_text = head_file(repo_dir, head, path)
            for n, name in dependency_names(path, change["added"], head_text):
                if name.lower() not in dependencies:
                    report.add(
                        "dependency-added",
                        path,
                        n,
                        f"{name} is new; name it on a Dependencies: line.",
                    )
        removed = any(REMOVED_TEST.match(t) for t in change["removed"])
        if removed and not tests_removed:
            report.add("test-removed", path, 0)
        if path.startswith(SOURCE_DIRS):
            source_changed.append(path)
        if TEST_PATH.search(path) and change["added"]:
            test_lines_added = True
    if (
        source_changed
        and not test_lines_added
        and "no test because" not in body.lower()
    ):
        report.add("fix-without-test", source_changed[0], 0)


def check_text(report, path, text, with_caps):
    """Apply the text rules to a block of text such as the PR body."""
    for n, line in enumerate(text.splitlines(), 1):
        check_typography_line(report, path, n, line)
        check_prose_line(report, path, n, line, True, with_caps)
        if ATTRIBUTION.search(line):
            report.add("attribution", path, n)


def check_commits(report, repo_dir, base, head):
    """Apply the text rules to every commit message between base and head."""
    out = git(
        repo_dir, "log", "--no-merges", "--format=%B%x1e", f"{base}..{head}"
    )
    messages = [m.strip("\n") for m in out.split("\x1e") if m.strip()]
    for ordinal, message in enumerate(reversed(messages), 1):
        for line in message.splitlines():
            check_typography_line(report, "commits", ordinal, line)
            check_prose_line(report, "commits", ordinal, line, True, False)
            if ATTRIBUTION.search(line):
                report.add("attribution", "commits", ordinal)


def run(
    repo_dir,
    base=None,
    head="HEAD",
    pr_body="",
    repo_name=None,
    standards_root=None,
):
    """Run every applicable rule and return the findings."""
    report = Report(load_exempt(standards_root, repo_name))
    allowlist = load_allowlist(standards_root, repo_name)
    check_tree(report, repo_dir, allowlist)
    # Only the hosted check passes a standards checkout; pre-commit may lag.
    if standards_root:
        for path, message in shared_files.findings(repo_dir):
            report.add("standards-copy", path, 0, message)
    if base:
        check_diff(report, repo_dir, base, head, pr_body or "")
        check_commits(report, repo_dir, base, head)
    if pr_body:
        check_text(report, "pull-request-body", pr_body, False)
    return sorted(report.findings, key=lambda f: (f.path, f.line, f.rule))


def print_findings(findings):
    """Print one line per finding, plus a GitHub annotation when in Actions."""
    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    for f in findings:
        level = "error" if f.blocks else "warning"
        rule = rules.BY_ID[f.rule]
        print(f"{f.path}:{f.line}: {level}: {f.rule}: {rule.rule} {f.message}")
        if annotate and f.path not in ("commits", "pull-request-body"):
            print(
                f"::{level} file={f.path},line={max(f.line, 1)},"
                f"title={f.rule}::{f.message}"
            )


def main(argv=None):
    """Command line entry point; returns 1 when any finding blocks."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-dir", default=".")
    parser.add_argument(
        "--base",
        help="base commit of the pull request; omit to run tree rules only",
    )
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--pr-body", help="file holding the pull request text")
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="owner/name, used to find the repo's entry under overrides/",
    )
    parser.add_argument(
        "--standards-root",
        help="checkout of the standards repo holding overrides/",
    )
    args = parser.parse_args(argv)
    body = ""
    if args.pr_body:
        body = Path(args.pr_body).read_text(encoding="utf-8")
    findings = run(
        args.repo_dir,
        args.base,
        args.head,
        body,
        args.repo,
        args.standards_root,
    )
    print_findings(findings)
    blocking = sum(f.blocks for f in findings)
    warnings = len(findings) - blocking
    print(f"{blocking} blocking finding(s), {warnings} warning(s)")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())

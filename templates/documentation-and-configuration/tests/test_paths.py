"""Every path a document names exists, and every relative link resolves.

A document is any Markdown file git tracks or would track. A backticked word
names a path when it ends in a slash or carries the extension of a file in the
repository. Fenced code is not read.
"""

import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKTICK = re.compile(r"`([^`\n]+)`")
INLINE_LINK = re.compile(r"\[[^\]\n]*\]\(\s*<?([^)\s>]+)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]\n]+\]:\s*<?([^\s>]+)")
NEVER_IN_A_PATH = set("<>{}*()=|$~@:\\ ")


def repository_files(pattern="*"):
    """Return the files git tracks or would track, relative to the root."""
    listing = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            pattern,
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    return [path for path in listing.split("\0") if (ROOT / path).is_file()]


DOCUMENTS = repository_files("*.md")
EXTENSIONS = {
    PurePosixPath(path).suffix.lower() for path in repository_files()
}


def prose_lines(document):
    """Return the document's lines that sit outside fenced code."""
    lines = []
    in_fence = False
    for line in (ROOT / document).read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        elif not in_fence:
            lines.append(line)
    return lines


def names_a_path(word):
    """Whether a backticked word names a file or a folder."""
    if NEVER_IN_A_PATH & set(word) or word.startswith(("-", "http")):
        return False
    if word.endswith("/"):
        return len(word) > 1
    suffix = PurePosixPath(word).suffix.lower()
    return suffix != "" and suffix in EXTENSIONS


def named_paths(document):
    """Return each path the document names in backticks."""
    words = []
    for line in prose_lines(document):
        for word in BACKTICK.findall(line):
            word = word.strip().removeprefix("./")
            if names_a_path(word):
                words.append(word)
    return words


def relative_links(document):
    """Return the target of each link that points inside the repository."""
    targets = []
    for line in prose_lines(document):
        line = BACKTICK.sub("", line)
        found = INLINE_LINK.findall(line) + REFERENCE_LINK.findall(line)
        for target in found:
            target = unquote(target.split("#")[0].split("?")[0])
            if target and ":" not in target:
                targets.append(target)
    return targets


def test_the_readme_is_among_the_documents():
    """The search finds the README, so the tests below have files to read."""
    assert "README.md" in DOCUMENTS


@pytest.mark.parametrize("document", DOCUMENTS)
def test_named_paths_exist(document):
    """A backticked path is found from the root or the document's folder."""
    folder = (ROOT / document).parent
    missing = [
        word
        for word in named_paths(document)
        if not (ROOT / word).exists() and not (folder / word).exists()
    ]
    assert not missing, f"{document} names paths that do not exist: {missing}"


@pytest.mark.parametrize("document", DOCUMENTS)
def test_relative_links_resolve(document):
    """A link target is found from the document's folder, or the root."""
    folder = (ROOT / document).parent
    broken = [
        target
        for target in relative_links(document)
        if not (
            ROOT / target.lstrip("/")
            if target.startswith("/")
            else folder / target
        ).exists()
    ]
    assert not broken, f"{document} links to files that do not exist: {broken}"

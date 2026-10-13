"""Every JSON file a tool reads is valid and names only files that exist.

A manifest is any JSON file git tracks or would track. A string in it names a
file when it starts with ./ or ../, or when it has no spaces and carries the
extension of a file in the repository. The file is looked for from the
manifest's folder and from each folder above it, up to the root.
"""

import json
from pathlib import PurePosixPath

import pytest
from test_paths import EXTENSIONS, NEVER_IN_A_PATH, ROOT, repository_files

MANIFESTS = repository_files("*.json")


def strings_in(value):
    """Yield every string held anywhere inside a parsed JSON value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings_in(item)


def names_a_file(text):
    """Whether a string in a manifest names a file or a folder."""
    if "://" in text or "\n" in text:
        return False
    if text.startswith(("./", "../")):
        return True
    suffix = PurePosixPath(text).suffix.lower()
    return (
        not NEVER_IN_A_PATH & set(text)
        and suffix != ""
        and suffix in EXTENSIONS
    )


def found_from(manifest, name):
    """Whether the name exists under the manifest's folder or one above it."""
    folder = (ROOT / manifest).parent
    while True:
        if (folder / name).exists():
            return True
        if folder == ROOT:
            return False
        folder = folder.parent


@pytest.mark.parametrize("manifest", MANIFESTS)
def test_manifest_is_valid_json(manifest):
    """The file parses as JSON."""
    try:
        json.loads((ROOT / manifest).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        pytest.fail(f"{manifest} is not valid JSON: {error}")


@pytest.mark.parametrize("manifest", MANIFESTS)
def test_manifest_names_files_that_exist(manifest):
    """Every file the manifest names is in the repository."""
    content = json.loads((ROOT / manifest).read_text(encoding="utf-8"))
    missing = [
        text
        for text in strings_in(content)
        if names_a_file(text) and not found_from(manifest, text)
    ]
    assert not missing, f"{manifest} names files that do not exist: {missing}"

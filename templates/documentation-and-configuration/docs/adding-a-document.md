# Adding a document

Every document beyond the README lives in this folder, one topic per file, with a file name that
says what the document holds.

## Naming files and folders in a document

Put a file or folder name in backticks, written from the top of the repository or from the folder
the document is in. The test in `tests/test_paths.py` reads every backticked name that ends in a
slash or in a file extension, and fails when the file or folder is not there. So a document cannot
keep describing a file after the file is renamed or removed.

To write about a file that does not exist yet, describe it in words and leave the backticks off.

## Linking to another document

Link to another document with a path from the folder this document is in. A link back to the README
from here looks like this:

```text
[the README](../README.md)
```

The same test follows every link that points inside the repository and fails when the target is
missing. Links to web addresses are not followed.

## Files a tool reads

The settings a tool reads stay in that tool's own folder. When one of them is a JSON file,
`tests/test_manifest.py` checks that it is valid and that every file it names exists.

## Before you commit

Run the tests from the top of the repository:

```text
pytest tests
```

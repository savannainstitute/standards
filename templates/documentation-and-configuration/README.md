# Repository name

One paragraph on what these documents and settings are for, who reads them,
and which tool reads the settings.

## Layout

- `docs/`: every document beyond this file. `docs/adding-a-document.md` says
  how to add one so the tests pass.
- A folder named for the tool holds the files that tool reads, laid out the
  way the tool requires. Prose about the tool goes under `docs/`.
- `tests/`: two tests that keep the documents and the settings honest.
  `tests/test_paths.py` checks that every path a document names exists and
  that every link to another file in this repository leads somewhere.
  `tests/test_manifest.py` checks that every JSON file is valid and names only
  files that exist.

## Running the tests

You need Python and git. Install pytest once, then run the tests from this
folder:

```text
pip install pytest
pytest tests
```

A failing test names the document and the path or link to fix.

## Checks

Every pull request runs the organization's checks, which include the two
tests. To run the rest of the checks before each commit:

```text
pip install pre-commit
pre-commit install
```

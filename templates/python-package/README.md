# Package name

One paragraph on what this package does, what it reads and returns, and who uses it.

## Installing it

Install the package from GitHub, naming the version. Replace the repository name with this
repository's name and `packagename` with the name in `pyproject.toml`:

```text
pip install "packagename @ git+https://github.com/savannainstitute/repository-name@v0.1.0"
```

The package starts with one small function, `plot_means()`, as a working pattern to replace: it
takes rows of measurements and returns the mean for each plot. It also has a command, `packagename`,
that runs that function over a CSV file. Rename the folder under `src/` and the name in
`pyproject.toml` to your package's name when you start.

## Layout

- `pyproject.toml`: the package's name, version, the packages it needs and its command. The one list
  of dependencies; nothing else lists them.
- `src/packagename/`: the code, one file per topic. `src/packagename/__main__.py` is the command;
  `src/packagename/__init__.py` reads the version from the installed metadata and holds nothing
  else.
- `tests/`: one test file per file in `src/packagename/`. Every expected number in a test carries a
  comment deriving it from the planted input. `tests/conftest.py` holds shared fixtures and never
  touches the import path. A test that needs a display, a device or a licensed program carries the
  marker `@pytest.mark.needs("what it needs")`.
- `docs/`: anything longer than this file. `docs/releasing.md` says how a version is released.
- `CHANGELOG.md`: one entry per released version.
- A data folder under `tests/`, when the package reads files, holds real sample files, each named
  for where it came from.

## Working on it

Create an environment, install the package in it with its test extras, and run the tests:

```text
python -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

## Checks

Every pull request runs the organization's checks. To run them before committing:

```text
pip install pre-commit
pre-commit install
```

## Large files

Images, rasters, point clouds, video, models, archives, PDFs and R data files are stored through Git
LFS, which keeps the repository small; `.gitattributes` lists the file types. Install it once on
your computer, before the first commit of such a file:

```text
git lfs install
```

A large or growing collection, such as the tiles from every flight, lives in object storage, and the
README says where.

## Coding agents

`AGENTS.md` holds the organization's rules for coding agents, and `CLAUDE.md`, the `.claude` folder
and the `.gemini` folder make Claude Code and Gemini read it. The `.claude`, `.codex` and `.gemini`
folders also run the organization's hook when the agent ends its turn. Add notes about this package
below the marker line in `AGENTS.md`; leave the rest as it is, because the check compares it with
the organization's copy.

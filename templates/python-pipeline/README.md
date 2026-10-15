# Pipeline name

One paragraph on what this pipeline produces, from which inputs, for whom.

## Inputs and outputs

`data/README.md` says where each input comes from and how to fetch it. Inputs go under the data
folder's inputs subfolder and are never modified; everything the pipeline writes goes under its
outputs subfolder.

## Running it

Create the environment once, then run the pipeline through its command:

```text
conda env create -f environment.yml
conda activate pipeline
pipeline --help
```

Each stage is a subcommand. The command name and the stages are declared in `pyproject.toml`.

## Layout

- `src/pipeline/`: the code, one module per stage, with `src/pipeline/cli.py` as the entry point.
  Rename the folder and the `name` in `pyproject.toml` to your pipeline's name when you start.
- `tests/`: one test file per stage. Every expected number in a test carries a comment deriving it
  from the planted input.
- A notebooks folder, when one is needed, holds walkthroughs only. Outputs are cleared before a
  notebook is committed.
- A docs folder holds anything longer than this file.
- `data/`: inputs and outputs, described in `data/README.md`.

## Checks

Every pull request runs the organization's checks. To run them before committing:

```text
pip install pre-commit
pre-commit install
```

## Coding agents

`AGENTS.md` holds the organization's rules for coding agents, and `CLAUDE.md`, the `.claude` folder
and the `.gemini` folder make Claude Code and Gemini read it. The `.claude`, `.codex` and `.gemini`
folders also run the organization's hook when the agent ends its turn. Add notes about this pipeline
below the marker line in `AGENTS.md`; leave the rest as it is, because the check compares it with
the organization's copy.

## Large files

Images, rasters, point clouds, video, models, archives, PDFs and R data files are stored through Git
LFS, which keeps the repository small; `.gitattributes` lists the file types. Install it once on
your computer, before the first commit of such a file:

```text
git lfs install
```

A large or growing collection, such as the tiles from every flight, lives in object storage, and
`data/README.md` says where.

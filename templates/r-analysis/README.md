# Analysis name

One paragraph on the question this analysis answers, the inputs it starts from and the
figures and tables it produces.

## Setting up

Open R in this folder and run this once. It records the packages the analysis uses, with
their versions, in a file named renv.lock, and writes the files that make R use those versions
in this folder:

```text
install.packages("renv")
renv::init()
```

Commit the files it creates. On another computer, `renv::restore()` installs the same
versions. After you add or update a package, run `renv::snapshot()` and commit the change.
The pull request check installs packages from renv.lock, so the tests cannot pass there until
that file is committed.

## Running it

`data/README.md` says where each input comes from and where to put it. Then, from this folder:

```text
Rscript run.R
```

`run.R` runs the scripts in order. It is the one way the analysis is run.

## Layout

- `R/`: functions only, one file per topic. Nothing in this folder does any work when it is
  loaded; the scripts call the functions.
- `scripts/`: the analysis, one numbered file per step, in the order they run. Each script
  reads from the data folder and writes its results back there or to an output folder.
- `run.R`: the list of scripts in run order. Add a line when you add a script.
- `tests/testthat/`: tests for the functions in `R/`, one test file per file there. A file
  whose name starts with `helper` builds the small tables the tests use, with the reason for
  each value written beside it. Every expected number carries a comment deriving it.
- `data/`: inputs and computed tables, described in `data/README.md`.
- An output folder holds the figures and tables this file refers to.
- A docs folder holds anything longer than this file.

The folder starts with one small function, one script and one test as a working pattern to
replace.

## Before you commit

Run the tests, then format the code with Air, which has to be installed once from
<https://posit-dev.github.io/air/>:

```text
Rscript tests/testthat.R
air format .
```

## Checks

Every pull request runs the organization's checks: the code is formatted the way Air formats
it, lintr finds no problems, and the tests pass. A failing check prints the file, the line and
what to change. The check tests the functions; it does not run the whole analysis.

Two more checks run when you commit, once you have installed pre-commit:

```text
pip install pre-commit
pre-commit install
```

## Tests the check cannot run

A test that needs a GPU, a licensed program, another operating system or an outside service
says so on its first line:

```text
test_that("the download matches the published table", {
  needs("access to the data server")
  ...
})
```

The check leaves that test out and prints the reason. On your own computer every test runs.
The function comes from `tests/testthat/helper-needs.R`; leave that file as it is.

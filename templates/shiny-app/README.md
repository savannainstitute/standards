# App name

One paragraph on what this app is for, who uses it, and the address where it is published.

## Setting up

Open R in this folder and run this once. It records the packages the app uses, with their
versions, in a file named renv.lock, and writes the files that make R use those versions in
this folder:

```text
install.packages("renv")
renv::init()
```

Commit the files it creates. On another computer, `renv::restore()` installs the same
versions. After you add or update a package, run `renv::snapshot()` and commit the change.
The pull request check installs packages from renv.lock, so the tests cannot pass there until
that file is committed.

## Running it on your computer

Open R in this folder and run:

```text
shiny::runApp()
```

## Publishing

The hosting service installs what a file named manifest.json lists, and publishes the app
again each time the main branch changes. Write that file with the command below and commit
it, and do so again whenever `renv::snapshot()` changes the packages:

```text
rsconnect::writeManifest()
```

There is no deploy step in this repository and no password or token stored with it.

## Layout

- `app.R`: the entry point. It holds one line and loads nothing itself.
- `R/`: everything else. Shiny loads every file in this folder when the app starts.
  `R/ui.R` is the page and `R/server.R` is what happens when someone uses it. A calculation
  goes in a function of its own so a test can call it without opening a browser.
- `tests/testthat/`: `tests/testthat/test-server.R` tests the calculation and the server
  without a browser, and `tests/testthat/test-app.R` starts the whole app once in a browser
  with no window, so a broken app cannot pass on the other tests alone. Every expected value
  carries a comment deriving it.
- A folder named www, when one is needed, holds images and style files the page shows.
- A data folder, when the app reads data, holds it with a file describing where each
  table comes from, its date, its license and its units.
- A docs folder holds anything longer than this file.

The app starts as a small working pattern to replace: two spacings typed in, and the number of
trees per hectare they give.

## Before you commit

Run the tests, then format the code with Air, which has to be installed once from
<https://posit-dev.github.io/air/>. The browser test needs Chrome on your computer:

```text
Rscript tests/testthat.R
air format .
```

## Checks

Every pull request runs the organization's checks: the code is formatted the way Air formats
it, lintr finds no problems, and the tests pass. A failing check prints the file, the line and
what to change.

Two more checks run when you commit, once you have installed pre-commit:

```text
pip install pre-commit
pre-commit install
```

## Tests the check cannot run

A test that needs a GPU, a licensed program, another operating system or an outside service
says so on its first line:

```text
test_that("the table loads from the data server", {
  needs("access to the data server")
  ...
})
```

The check leaves that test out and prints the reason. On your own computer every test runs.
The function comes from `tests/testthat/helper-needs.R`; leave that file as it is.

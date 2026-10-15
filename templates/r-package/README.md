# Package name

One paragraph on what this package does, what it reads and returns, and who uses it.

## Using it

Install the package from GitHub, then load it. Replace the repository name with this repository's
name and `packagename` with the name in `DESCRIPTION`:

```text
install.packages("pak")
pak::pak("savannainstitute/repository-name")
library(packagename)
```

The package starts with one small function, `plot_means()`, as a working pattern to replace: it
takes a table of measurements and returns the mean for each plot. Rename the package in
`DESCRIPTION`, in `tests/testthat.R` and in `NEWS.md` when you start, and replace the first author
line in `DESCRIPTION`, which holds a stand-in name and address, with your own.

## Layout

- `DESCRIPTION`: the package's name, version, authors and the packages it needs. A package you use
  goes under Imports; one only the tests use goes under Suggests.
- `R/`: the code, one file per topic. The comment lines starting with `#'` above a function are its
  help page.
- `man/` and `NAMESPACE`: written by roxygen2 from those comment lines. Never edit them by hand; run
  the command under "Before you commit" instead.
- `tests/testthat/`: one test file per file in `R/`. A file whose name starts with `helper` builds
  the small tables the tests use, with the reason for each value written beside it. Every expected
  number in a test carries a comment deriving it from those values.
- `NEWS.md`: one entry per released version.
- `LICENSE`: the year and the copyright holder of the MIT license, in the two-line form R expects.
- A vignettes folder, when one is needed, holds long-form guides as R Markdown or Quarto sources.
  Rendered PDF and HTML files are not committed.
- A data-raw folder holds the scripts that build any data the package ships. Data the package
  exports goes in a data folder, and small raw files that tests read go under inst/extdata.
- A docs folder holds anything longer than this file.

## Before you commit

Run these three commands from the repository folder. The first rewrites the help pages, the second
runs the tests, and the third formats the code with Air, which has to be installed once from
<https://posit-dev.github.io/air/>:

```text
Rscript -e "roxygen2::roxygenise()"
Rscript -e "testthat::test_local()"
air format .
```

## Checks

Every pull request runs the organization's checks: the code is formatted the way Air formats it,
lintr finds no problems, the help pages match the code, and the tests pass. A failing check prints
the file, the line and what to change.

Two more checks run when you commit, once you have installed pre-commit:

```text
pip install pre-commit
pre-commit install
```

## Tests the check cannot run

A test that needs a GPU, a licensed program, another operating system or an outside service says so
on its first line:

```text
test_that("the download matches the published table", {
  needs("access to the data server")
  ...
})
```

The check leaves that test out and prints the reason. On your own computer every test runs. The
function comes from `tests/testthat/helper-needs.R`; leave that file as it is.

## Large files

Images, rasters, point clouds, video, models, archives, PDFs and R data files are stored through Git
LFS, which keeps the repository small; `.gitattributes` lists the file types. Install it once on
your computer, before the first commit of such a file:

```text
git lfs install
```

A large or growing collection, such as the tiles from every flight, lives in object storage, and the
README says where.

#' Measure line coverage of R/ by tests/testthat/ and write a Cobertura file;
#' usage: Rscript run_coverage.R <repo_dir> <out.xml>.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 2L || !dir.exists(arguments[[1L]])) {
  stop("usage: Rscript run_coverage.R <repo_dir> <out.xml>", call. = FALSE)
}
repo_dir <- normalizePath(arguments[[1L]], winslash = "/")
out <- arguments[[2L]]

# Packages installed for the check alone are found after the repository's own.
tools_library <- Sys.getenv("STANDARDS_R_LIB")
if (nzchar(tools_library)) {
  .libPaths(c(.libPaths(), tools_library))
}

Sys.setenv(NOT_CRAN = "true")
# Attached so that test files outside a package find test_that() and friends.
library(testthat) # nolint: unused_import_linter. The test files use it.

tests_dir <- file.path(repo_dir, "tests", "testthat")
if (!dir.exists(tests_dir)) {
  cat("No testthat folder; nothing to measure.\n")
  quit(status = 0L)
}

if (file.exists(file.path(repo_dir, "DESCRIPTION"))) {
  coverage <- covr::package_coverage(repo_dir, type = "tests", quiet = TRUE)
} else {
  # The files under R/ are traced, then the tests run with them in scope.
  source_files <- list.files(
    file.path(repo_dir, "R"),
    pattern = "[.][Rr]$",
    full.names = TRUE
  )
  if (length(source_files) == 0L) {
    cat("No files under R/; nothing to measure.\n")
    quit(status = 0L)
  }
  runner <- tempfile(fileext = ".R")
  writeLines(
    c(
      sprintf(
        "testthat::test_dir(%s, env = environment(),",
        deparse(tests_dir)
      ),
      "  stop_on_failure = FALSE, reporter = 'summary')"
    ),
    runner
  )
  # The templates' helpers load R/ themselves unless this says it is loaded.
  Sys.setenv(STANDARDS_CODE_LOADED = "true")
  old <- setwd(tests_dir)
  coverage <- covr::file_coverage(
    source_files,
    runner,
    parent_env = globalenv()
  )
  setwd(old)
}

print(coverage)
dir.create(dirname(out), showWarnings = FALSE, recursive = TRUE)
covr::to_cobertura(coverage, filename = out)
cat("wrote", out, "\n")

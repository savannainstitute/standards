#' Run tests/testthat/ of a package or of any other repository, print how
#' many tests needs() left out and why, and exit with status 1 as coded below.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 1L || !dir.exists(arguments[[1L]])) {
  stop("usage: Rscript run_tests.R <repo_dir>", call. = FALSE)
}
repo_dir <- normalizePath(arguments[[1L]])

# Packages installed for the check alone are found after the repository's own.
tools_library <- Sys.getenv("STANDARDS_R_LIB")
if (nzchar(tools_library)) {
  .libPaths(c(.libPaths(), tools_library))
}

tests_dir <- file.path(repo_dir, "tests", "testthat")
if (!dir.exists(tests_dir)) {
  stop(repo_dir, " has no tests/testthat folder", call. = FALSE)
}

# Attached so that test files outside a package find test_that() and friends.
library(testthat)

description_file <- file.path(repo_dir, "DESCRIPTION")
if (file.exists(description_file)) {
  package <- unname(read.dcf(description_file, fields = "Package")[1L, 1L])
  results <- test_dir(
    tests_dir,
    package = package,
    load_package = "source",
    stop_on_failure = FALSE
  )
} else {
  results <- test_dir(tests_dir, stop_on_failure = FALSE)
}

has_class <- function(expectations, class) {
  vapply(expectations, inherits, logical(1L), what = class)
}

broken <- character()
needs_reasons <- character()
other_skips <- character()
for (test in results) {
  label <- paste0(test$file, ": ", test$test)
  expectations <- test$results
  failed <- has_class(expectations, "expectation_failure")
  errored <- has_class(expectations, "expectation_error")
  if (any(failed | errored)) {
    broken <- c(broken, label)
  }
  for (skipped in expectations[has_class(expectations, "expectation_skip")]) {
    reason <- sub("^Reason: ", "", conditionMessage(skipped))
    if (startsWith(reason, "needs: ")) {
      needs_reasons <- c(needs_reasons, sub("^needs: ", "", reason))
    } else {
      other_skips <- c(other_skips, paste0(label, ": ", reason))
    }
  }
}

if (length(needs_reasons) > 0L) {
  cat(
    length(needs_reasons),
    "test(s) left out because they need:",
    paste(sort(unique(needs_reasons)), collapse = "; "),
    "\n"
  )
}
if (length(other_skips) > 0L) {
  cat("Skipped without needs(); mark the test with needs(\"a reason\"):\n")
  cat(paste0("  ", other_skips), sep = "\n")
}
if (length(broken) > 0L) {
  cat("Failed:\n")
  cat(paste0("  ", broken), sep = "\n")
}
if (length(results) == 0L) {
  cat("No test ran in", tests_dir, "\n")
}
if (length(results) == 0L || length(broken) + length(other_skips) > 0L) {
  quit(status = 1L)
}

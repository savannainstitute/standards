#' Mark a test the hosted check cannot run: call needs("what it needs") on the
#' first line of a test_that() block. On your own machine every test runs.
needs <- function(reason) {
  one_string <- !missing(reason) && is.character(reason) && length(reason) == 1L
  if (!one_string || is.na(reason) || !nzchar(trimws(reason))) {
    stop("needs() requires a reason, such as needs(\"a GPU\")", call. = FALSE)
  }
  # The hosted check sets this variable; the skip message is what it counts.
  if (identical(Sys.getenv("STANDARDS_NO_NEEDS"), "true")) {
    testthat::skip(paste0("needs: ", reason))
  }
  invisible(NULL)
}

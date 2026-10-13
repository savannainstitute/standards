run_planted <- function(test_lines) {
  repo <- withr::local_tempdir(.local_envir = parent.frame())
  tests <- file.path(repo, "tests", "testthat")
  dir.create(tests, recursive = TRUE)
  helper <- test_path("..", "..", "src", "standards", "r", "helper-needs.R")
  file.copy(helper, file.path(tests, "helper-needs.R"))
  writeLines(test_lines, file.path(tests, "test-planted.R"))
  script <- test_path("..", "..", "src", "standards", "r", "run_tests.R")
  output <- suppressWarnings(system2(
    file.path(R.home("bin"), "Rscript"),
    c(shQuote(normalizePath(script)), shQuote(repo)),
    stdout = TRUE,
    stderr = TRUE,
    env = "STANDARDS_NO_NEEDS=true"
  ))
  status <- attr(output, "status")
  list(status = if (is.null(status)) 0L else status, output = output)
}

test_that("a passing test and a needs() test pass and print the reason", {
  result <- run_planted(c(
    "test_that('adds', expect_identical(1 + 1, 2))",
    "test_that('gpu', {",
    "  needs('a GPU')",
    "  expect_identical(2 * 2, 4)",
    "})"
  ))
  expect_identical(result$status, 0L)
  expect_true(any(grepl(
    "1 test(s) left out because they need: a GPU",
    result$output,
    fixed = TRUE
  )))
})

test_that("a skip without needs() fails the run", {
  result <- run_planted("test_that('later', skip('not yet'))")
  expect_identical(result$status, 1L)
  expect_true(any(grepl(
    "Skipped without needs()",
    result$output,
    fixed = TRUE
  )))
})

test_that("a failing test fails the run", {
  result <- run_planted("test_that('wrong', expect_identical(1, 2))")
  expect_identical(result$status, 1L)
  expect_true(any(grepl("Failed:", result$output, fixed = TRUE)))
})

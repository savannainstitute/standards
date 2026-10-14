run_lintr_on <- function(files) {
  repo <- withr::local_tempdir(.local_envir = parent.frame())
  for (name in names(files)) {
    path <- file.path(repo, name)
    dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
    writeLines(files[[name]], path)
  }
  script <- testthat::test_path(
    "..",
    "..",
    "src",
    "standards",
    "r",
    "run_lintr.R"
  )
  output <- suppressWarnings(system2(
    file.path(R.home("bin"), "Rscript"),
    c(shQuote(normalizePath(script)), shQuote(repo)),
    stdout = TRUE,
    stderr = TRUE
  ))
  status <- attr(output, "status")
  list(status = if (is.null(status)) 0L else status, output = output)
}

# A line as renv writes it: trailing whitespace and over 80 columns.
renv_line <- paste0("  x <- '", strrep("a", 80), "'   ")
clean_function <- "add <- function(a, b) {\n  a + b\n}"

test_that("renv's activation script is skipped at any depth", {
  files <- list(clean_function, renv_line, renv_line)
  names(files) <- c(
    file.path("R", "clean.R"),
    file.path("renv", "activate.R"),
    file.path("templates", "analysis", "renv", "activate.R")
  )
  result <- run_lintr_on(files)
  expect_identical(result$status, 0L)
  expect_true(any(grepl("0 lint(s)", result$output, fixed = TRUE)))
})

test_that("a lint in an ordinary file still fails the run", {
  files <- list(renv_line)
  names(files) <- file.path("R", "messy.R")
  result <- run_lintr_on(files)
  expect_identical(result$status, 1L)
  expect_true(any(grepl(
    "line_length_linter",
    result$output,
    fixed = TRUE
  )))
})

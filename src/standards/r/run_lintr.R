#' Lint a package or a plain directory with the organization's linter list,
#' ignoring the repository's own lintr settings; any lint exits with status 1.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 1L || !dir.exists(arguments[[1L]])) {
  stop("usage: Rscript run_lintr.R <repo_dir>", call. = FALSE)
}
repo_dir <- normalizePath(arguments[[1L]])

# Packages installed for the check alone are found after the repository's own.
tools_library <- Sys.getenv("STANDARDS_R_LIB")
if (nzchar(tools_library)) {
  .libPaths(c(.libPaths(), tools_library))
}

file_argument <- grep("^--file=", commandArgs(), value = TRUE)
script_dir <- dirname(sub("^--file=", "", file_argument))
source(file.path(script_dir, "lintr_settings.R"))

is_package <- file.exists(file.path(repo_dir, "DESCRIPTION"))
lint_repo <- if (is_package) lintr::lint_package else lintr::lint_dir
default_exclusions <- if (is_package) {
  list(file.path("R", "RcppExports.R"))
} else {
  list("renv", "packrat")
}

# renv writes activate.R and rewrites it on update; skipped wherever it sits.
renv_scripts <- list.files(
  repo_dir,
  pattern = "^activate[.]R$",
  recursive = TRUE
)
renv_scripts <- renv_scripts[basename(dirname(renv_scripts)) == "renv"]

lints <- lint_repo(
  repo_dir,
  linters = central_linters,
  parse_settings = FALSE,
  exclusions = c(default_exclusions, as.list(renv_scripts))
)

for (lint in lints) {
  cat(lint$filename, ":", lint$line_number, ": ", sep = "")
  cat(lint$message, " [", lint$linter, "]\n", sep = "")
}
cat(length(lints), "lint(s)\n")
if (length(lints) > 0L) {
  quit(status = 1L)
}

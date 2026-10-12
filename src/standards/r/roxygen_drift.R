#' Regenerate a package's man/ and NAMESPACE with roxygen2 and exit with
#' status 1, naming the stale files, when git shows that either changed.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 1L || !dir.exists(arguments[[1L]])) {
  stop("usage: Rscript roxygen_drift.R <repo_dir>", call. = FALSE)
}
repo_dir <- normalizePath(arguments[[1L]])

description_file <- file.path(repo_dir, "DESCRIPTION")
if (!file.exists(description_file)) {
  stop(
    repo_dir,
    " has no DESCRIPTION file; this check is for R packages",
    call. = FALSE
  )
}

description <- read.dcf(description_file)
version_fields <- intersect(
  c("Config/roxygen2/version", "RoxygenNote"),
  colnames(description)
)
if (length(version_fields) == 0L) {
  stop(
    "DESCRIPTION records no roxygen2 version; run roxygen2::roxygenise() ",
    "and commit what it writes",
    call. = FALSE
  )
}

# Another roxygen2 version can write different files from the same source.
recorded <- unname(description[1L, version_fields[[1L]]])
installed <- as.character(utils::packageVersion("roxygen2"))
if (!identical(recorded, installed)) {
  stop(
    "DESCRIPTION records roxygen2 ",
    recorded,
    " and roxygen2 ",
    installed,
    " is installed; install the recorded version",
    call. = FALSE
  )
}

roxygen2::roxygenise(repo_dir)

git_arguments <- c(
  "-C",
  shQuote(repo_dir),
  "status",
  "--porcelain",
  "--",
  "man",
  "NAMESPACE"
)
stale <- system2("git", git_arguments, stdout = TRUE)
if (!is.null(attr(stale, "status"))) {
  stop("git status failed in ", repo_dir, call. = FALSE)
}

if (length(stale) > 0L) {
  cat("Generated documentation is stale. Run roxygen2::roxygenise() and\n")
  cat("commit these files:\n")
  cat(paste0("  ", stale), sep = "\n")
  quit(status = 1L)
}
cat("man/ and NAMESPACE match the source\n")

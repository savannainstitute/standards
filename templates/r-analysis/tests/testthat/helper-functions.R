# Tests run from this folder, so the functions are two folders up, in R/. The
# organization's coverage run loads them first and says so in this variable.
if (!nzchar(Sys.getenv("STANDARDS_CODE_LOADED"))) {
  for (path in list.files(test_path("..", "..", "R"), full.names = TRUE)) {
    source(path, local = TRUE)
  }
}

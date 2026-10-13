# Tests run from this folder, so the functions are two folders up, in R/.
for (path in list.files(test_path("..", "..", "R"), full.names = TRUE)) {
  source(path, local = TRUE)
}

# Loads the functions in R/, two folders up, so tests can call them directly.
shinytest2::load_app_support(test_path("..", ".."))

# With no DESCRIPTION file, the testthat edition is set here for every test.
local_edition(3, .env = teardown_env())

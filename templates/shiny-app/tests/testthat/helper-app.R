# Loads the functions in R/, two folders up, where every test can call them.
# The organization's coverage run loads them first and says so in this variable.
if (!nzchar(Sys.getenv("STANDARDS_CODE_LOADED"))) {
  shiny::loadSupport(test_path("..", ".."), renv = environment())
}

# With no DESCRIPTION file, the testthat edition is set here for every test.
local_edition(3, .env = teardown_env())

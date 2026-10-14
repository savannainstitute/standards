# Loads the functions in R/, two folders up, where every test can call them.
shiny::loadSupport(test_path("..", ".."), renv = environment())

# With no DESCRIPTION file, the testthat edition is set here for every test.
local_edition(3, .env = teardown_env())

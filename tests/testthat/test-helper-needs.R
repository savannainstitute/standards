source(
  test_path("..", "..", "src", "standards", "r", "helper-needs.R"),
  local = TRUE
)

test_that("needs() refuses a missing or blank reason", {
  expect_error(needs(), "requires a reason")
  expect_error(needs("  "), "requires a reason")
})

test_that("needs() does nothing when the check's variable is not true", {
  withr::local_envvar(STANDARDS_NO_NEEDS = "false")
  expect_null(needs("a GPU"))
})

test_that("needs() skips with the reason when the variable is true", {
  withr::local_envvar(STANDARDS_NO_NEEDS = "true")
  message <- tryCatch(
    needs("a GPU"),
    skip = function(condition) conditionMessage(condition)
  )
  expect_match(message, "needs: a GPU$")
})

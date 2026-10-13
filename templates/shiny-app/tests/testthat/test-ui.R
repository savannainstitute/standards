test_that("the page carries both inputs and the output the server fills", {
  html <- as.character(app_ui())
  expect_match(html, "row_spacing_m", fixed = TRUE)
  expect_match(html, "tree_spacing_m", fixed = TRUE)
  expect_match(html, "density", fixed = TRUE)
})

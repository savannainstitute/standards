test_that("trees per hectare follows from the two spacings", {
  # a tree every 5 m by 2 m takes 10 square meters, and 10000 over 10 is 1000
  expect_identical(trees_per_hectare(5, 2), 1000)
  # a spacing of zero gives no density, so the function stops
  expect_error(trees_per_hectare(0, 2), "greater than zero")
})

test_that("the server shows the density for the spacings typed in", {
  shiny::testServer(app_server, {
    session$setInputs(row_spacing_m = 5, tree_spacing_m = 2)
    # the same planted spacings give 1000, shown with a comma after the 1
    expect_identical(output$density, "1,000 trees per hectare")
  })
})

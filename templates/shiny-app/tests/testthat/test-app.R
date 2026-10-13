test_that("the app starts in a browser and shows the density", {
  app <- shinytest2::AppDriver$new(name = "start")
  app$set_inputs(row_spacing_m = 5, tree_spacing_m = 2)
  shown <- app$get_value(output = "density")
  app$stop()

  # a tree every 5 m by 2 m takes 10 square meters, and 10000 over 10 is 1000
  expect_identical(shown, "1,000 trees per hectare")
})

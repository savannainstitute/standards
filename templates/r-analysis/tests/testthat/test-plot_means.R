test_that("each plot gets the mean of its own trees", {
  result <- plot_means(planted_measurements(), "height_m", "plot")

  # the planted plots sort by name, north before south
  expect_identical(result$plot, c("north", "south"))
  # three trees were planted in each plot
  expect_identical(result$n, c(3L, 3L))
  # north holds 2, 4 and 6, which sum to 12, and 12 over 3 trees is 4
  expect_identical(result$mean[result$plot == "north"], 4)
  # south holds 1, 1 and 4, which sum to 6, and 6 over 3 trees is 2
  expect_identical(result$mean[result$plot == "south"], 2)
})

test_that("a blank measurement stops the calculation", {
  measurements <- planted_measurements()
  measurements$height_m[2] <- NA

  # one of the six planted heights was blanked, so the message counts one
  expect_error(
    plot_means(measurements, "height_m", "plot"),
    "1 missing value"
  )
})

test_that("a column that is not in the table is named", {
  # the planted table has no column called diameter_cm
  expect_error(
    plot_means(planted_measurements(), "diameter_cm", "plot"),
    "no column diameter_cm"
  )
})

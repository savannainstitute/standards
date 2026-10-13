#' Six trees in two plots, three in each, with heights chosen so that each
#' plot mean is a whole number a reader can work out by hand.
planted_measurements <- function() {
  data.frame(
    plot = c("north", "north", "north", "south", "south", "south"),
    height_m = c(2, 4, 6, 1, 1, 4)
  )
}

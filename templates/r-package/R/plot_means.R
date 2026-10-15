#' Mean of a measurement for each plot
#'
#' @param measurements A data frame with one row per measurement.
#' @param value Name of the numeric column to average.
#' @param plot Name of the column that says which plot each row belongs to.
#' @return A data frame with one row per plot: `plot`, `n` and `mean`.
#' @export
plot_means <- function(measurements, value, plot) {
  absent <- setdiff(c(value, plot), names(measurements))
  if (length(absent) > 0L) {
    stop("measurements has no column ", toString(absent), call. = FALSE)
  }
  values <- measurements[[value]]
  if (!is.numeric(values)) {
    stop(value, " is not a numeric column", call. = FALSE)
  }
  if (anyNA(values)) {
    stop(
      sum(is.na(values)),
      " missing value(s) in ",
      value,
      "; decide what a blank means before taking a mean",
      call. = FALSE
    )
  }
  by_plot <- split(values, measurements[[plot]])
  data.frame(
    plot = names(by_plot),
    n = lengths(by_plot, use.names = FALSE),
    mean = vapply(by_plot, mean, numeric(1L), USE.NAMES = FALSE)
  )
}

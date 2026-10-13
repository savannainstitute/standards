source(file.path("R", "plot_means.R"))

input <- file.path("data", "raw", "measurements.csv")
if (!file.exists(input)) {
  stop(input, " is missing; the README in data says how to get it")
}

measurements <- read.csv(input)
means <- plot_means(measurements, value = "height_m", plot = "plot")

derived <- file.path("data", "derived")
dir.create(derived, recursive = TRUE, showWarnings = FALSE)
write.csv(means, file.path(derived, "plot_means.csv"), row.names = FALSE)

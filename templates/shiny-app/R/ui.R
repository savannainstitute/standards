#' The page: two spacings to type in and the planting density they give.
app_ui <- function() {
  shiny::fluidPage(
    shiny::titlePanel("Trees per hectare"),
    shiny::numericInput("row_spacing_m", "Meters between rows", value = NA),
    shiny::numericInput(
      "tree_spacing_m",
      "Meters between trees in a row",
      value = NA
    ),
    shiny::textOutput("density")
  )
}

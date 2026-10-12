#' Trees planted per hectare at a spacing between rows and within a row,
#' both in meters.
trees_per_hectare <- function(row_spacing_m, tree_spacing_m) {
  if (row_spacing_m <= 0 || tree_spacing_m <= 0) {
    stop("both spacings must be greater than zero", call. = FALSE)
  }
  # A hectare is 10,000 square meters by definition.
  10000 / (row_spacing_m * tree_spacing_m)
}

#' The server: waits for both spacings, then shows the density as whole trees.
app_server <- function(input, output, session) {
  density <- shiny::reactive({
    shiny::req(input$row_spacing_m, input$tree_spacing_m)
    trees_per_hectare(input$row_spacing_m, input$tree_spacing_m)
  })
  output$density <- shiny::renderText({
    trees <- format(round(density()), big.mark = ",", scientific = FALSE)
    paste(trees, "trees per hectare")
  })
}

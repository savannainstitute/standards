#' The organization's linter list, read by run_lintr.R: lintr's defaults,
#' less the one that can disagree with the Air formatter, plus eight more.

central_linters <- lintr::linters_with_defaults(
  # Air indents chained assignments differently: posit-dev/air issue 444.
  indentation_linter = NULL,
  # 80 is the default here and in Air: lintr.r-lib.org/reference/linters.html
  line_length_linter = lintr::line_length_linter(80L),
  lintr::unused_import_linter(),
  lintr::unreachable_code_linter(),
  lintr::absolute_path_linter(),
  lintr::nonportable_path_linter(),
  lintr::missing_package_linter(),
  lintr::expect_true_false_linter(),
  lintr::expect_identical_linter(),
  lintr::yoda_test_linter()
)

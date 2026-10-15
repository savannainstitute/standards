"""plot_means() returns the derived means and refuses what it cannot judge."""

import pytest

from packagename.means import plot_means

# Three measurements in plot a (2, 4, 6) and one in plot b (10), as a reader
# of a CSV would hand them over: every value is a string.
ROWS = [
    {"plot": "a", "height": "2"},
    {"plot": "a", "height": "4"},
    {"plot": "a", "height": "6"},
    {"plot": "b", "height": "10"},
]


def test_means_per_plot():
    """(2 + 4 + 6) / 3 = 4 for plot a; 10 / 1 = 10 for plot b."""
    assert plot_means(ROWS, "height", "plot") == [
        {"plot": "a", "n": 3, "mean": 4.0},
        {"plot": "b", "n": 1, "mean": 10.0},
    ]


def test_an_empty_table_gives_no_rows():
    """No measurements, no means."""
    assert plot_means([], "height", "plot") == []


def test_a_missing_column_is_named():
    """The table has plot and height; width is absent."""
    with pytest.raises(ValueError, match="no column width"):
        plot_means(ROWS, "width", "plot")


def test_a_blank_value_stops_the_mean():
    """One blank among four rows is reported as one blank."""
    rows = ROWS + [{"plot": "b", "height": ""}]
    with pytest.raises(ValueError, match="1 blank value"):
        plot_means(rows, "height", "plot")


def test_a_non_numeric_column_is_refused():
    """The plot column holds letters, so it cannot be averaged."""
    with pytest.raises(ValueError, match="not a numeric column"):
        plot_means(ROWS, "plot", "height")

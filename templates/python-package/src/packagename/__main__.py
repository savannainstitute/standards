"""Command line entry point: python -m packagename, or the command."""

import argparse
import csv
import sys

from packagename import __version__
from packagename.means import plot_means


def build_parser():
    """Return the parser: a CSV file and the two column names."""
    parser = argparse.ArgumentParser(prog="packagename", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("table", help="CSV file with one row per measurement")
    parser.add_argument("--value", required=True, help="the measured column")
    parser.add_argument("--plot", required=True, help="the plot column")
    return parser


def main(argv=None):
    """Print the mean of the value for each plot in the table."""
    args = build_parser().parse_args(argv)
    with open(args.table, encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    for row in plot_means(rows, args.value, args.plot):
        print(f"{row['plot']}\t{row['n']}\t{row['mean']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

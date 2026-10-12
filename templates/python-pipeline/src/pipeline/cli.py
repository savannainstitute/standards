"""Command line entry point: one subcommand per pipeline stage."""

import argparse
import sys


def build_parser():
    """Return the argument parser with one subcommand per stage."""
    parser = argparse.ArgumentParser(prog="pipeline", description=__doc__)
    stages = parser.add_subparsers(dest="stage", required=True)
    prepare = stages.add_parser(
        "prepare", help="read the inputs and write the prepared files"
    )
    prepare.add_argument(
        "--inputs", required=True, help="folder holding the raw inputs"
    )
    prepare.add_argument(
        "--outputs", required=True, help="folder the stage writes to"
    )
    return parser


def main(argv=None):
    """Parse the arguments and run the chosen stage."""
    args = build_parser().parse_args(argv)
    if args.stage == "prepare":
        raise SystemExit("the prepare stage is not written yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())

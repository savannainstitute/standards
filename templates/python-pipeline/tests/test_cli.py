"""The command line parser reads each stage's arguments."""

from pipeline.cli import build_parser


def test_prepare_reads_both_folders(tmp_path):
    """The two folder arguments come back as the strings passed in."""
    inputs = tmp_path / "in"
    outputs = tmp_path / "out"
    args = build_parser().parse_args(
        ["prepare", "--inputs", str(inputs), "--outputs", str(outputs)]
    )
    assert args.stage == "prepare"
    assert args.inputs == str(inputs)
    assert args.outputs == str(outputs)

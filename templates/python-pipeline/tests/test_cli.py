"""The command line parser reads each stage's arguments."""

import pytest

from pipeline.cli import build_parser, main


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


def test_prepare_says_it_is_not_written(tmp_path):
    """The template's one stage stops with a message until it is written."""
    with pytest.raises(SystemExit, match="not written yet"):
        main(
            ["prepare", "--inputs", str(tmp_path), "--outputs", str(tmp_path)]
        )


def test_a_missing_stage_is_refused():
    """The parser exits with status 2 when no stage is named."""
    with pytest.raises(SystemExit) as stopped:
        main([])
    assert stopped.value.code == 2

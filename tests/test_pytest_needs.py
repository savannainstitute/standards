"""The needs marker deselects on --no-needs and requires a reason."""

import pytest

pytest_plugins = ["pytester"]

SUITE = """
import pytest


def test_plain():
    assert 1 + 1 == 2


@pytest.mark.needs("a GPU")
def test_gpu():
    assert 2 * 2 == 4
"""

NO_REASON = """
import pytest


@pytest.mark.needs
def test_x():
    assert 1 + 1 == 2
"""


def test_marker_deselected_with_option(pytester):
    pytester.makepyfile(test_suite=SUITE)
    result = pytester.runpytest(
        "-p", "standards.pytest_needs", "--no-needs", "--strict-markers", "-s"
    )
    result.assert_outcomes(passed=1, deselected=1)
    result.stdout.fnmatch_lines(
        ["*1 test(s) left out because they need: a GPU*"]
    )


def test_marker_runs_without_option(pytester):
    pytester.makepyfile(test_suite=SUITE)
    result = pytester.runpytest(
        "-p", "standards.pytest_needs", "--strict-markers"
    )
    result.assert_outcomes(passed=2)


def test_missing_reason_is_an_error(pytester):
    pytester.makepyfile(test_suite=NO_REASON)
    result = pytester.runpytest(
        "-p", "standards.pytest_needs", "--no-needs", "--strict-markers"
    )
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*needs() requires a reason*"])

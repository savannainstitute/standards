"""pytest plugin: the needs marker for tests the hosted check cannot run.

A test that needs a GPU, a licensed program, another operating system or an
outside service carries needs("what it needs"). With --no-needs those tests
are deselected, and the count and the reasons are printed so nobody mistakes
a smaller run for a full one. Without the option, on the owner's machine or
a self-hosted runner, every test runs.
"""

import pytest


def pytest_addoption(parser):
    """Add the --no-needs option."""
    parser.addoption(
        "--no-needs",
        action="store_true",
        default=False,
        help="deselect tests carrying the needs marker and print why",
    )


def pytest_configure(config):
    """Declare the needs marker so --strict-markers accepts it."""
    config.addinivalue_line(
        "markers",
        "needs(reason): the test cannot run on the hosted Linux check; "
        "the reason says what it needs",
    )


def pytest_collection_modifyitems(config, items):
    """Deselect the marked tests under --no-needs and print their reasons."""
    if not config.getoption("--no-needs"):
        return
    kept, deselected = [], []
    for item in items:
        marker = item.get_closest_marker("needs")
        if marker is None:
            kept.append(item)
            continue
        if not marker.args or not str(marker.args[0]).strip():
            raise pytest.UsageError(
                f"{item.nodeid}: needs() requires a reason"
            )
        deselected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept
        reasons = sorted(
            str(item.get_closest_marker("needs").args[0])
            for item in deselected
        )
        print(
            f"\n{len(deselected)} test(s) left out because they need: "
            + "; ".join(sorted(set(reasons)))
        )

"""The coverage gate passes and fails exactly where the floor says.

Every expected percentage below is counted by hand from the planted report.
"""

import pytest

from standards import coverage_gate

REPORT = """<?xml version="1.0" ?>
<coverage>
  <sources><source>{root}/src</source></sources>
  <packages><package><classes>
    <class filename="pkg/a.py"><lines>
      <line number="1" hits="1"/>
      <line number="2" hits="0"/>
      <line number="3" hits="2"/>
      <line number="4" hits="0"/>
    </lines></class>
    <class filename="pkg/b.py"><lines>
      <line number="1" hits="1"/>
      <line number="2" hits="1"/>
    </lines></class>
  </classes></package></packages>
</coverage>
"""


def lines_from(tmp_path):
    report = tmp_path / "coverage.xml"
    report.write_text(REPORT.format(root=tmp_path.as_posix()))
    return coverage_gate.load_lines(tmp_path, [report])


def test_paths_resolve_against_the_report_source(tmp_path):
    assert sorted(lines_from(tmp_path)) == ["src/pkg/a.py", "src/pkg/b.py"]


def test_total_counts_every_measured_line(tmp_path):
    """a.py covers 2 of 4 lines and b.py 2 of 2, so 4 of 6."""
    assert coverage_gate.total(lines_from(tmp_path)) == (4, 6)


def test_changed_counts_only_measured_added_lines(tmp_path):
    """Lines 2 and 3 of a.py are measured, one covered; line 9 is not code."""
    added = {"src/pkg/a.py": [2, 3, 9], "README.md": [1]}
    assert coverage_gate.changed(lines_from(tmp_path), added) == (1, 2)


@pytest.mark.parametrize(
    ("percent", "start", "changed", "passes", "words"),
    [
        (80.0, None, None, True, "80.0%"),
        (74.9, None, None, False, "75%"),
        (51.0, 52.0, (9, 10), False, "below the 52.0%"),
        (53.0, 52.0, (19, 20), True, "95.0% of the changed lines"),
        (53.0, 52.0, (8, 10), False, "80.0% of the changed lines"),
        (53.0, 52.0, (0, 0), True, "no changed line"),
        (76.0, 52.0, (0, 10), True, "76.0%"),
    ],
    ids=[
        "new-repo-above",
        "new-repo-below",
        "fell",
        "climbing",
        "changed-too-low",
        "no-code-changed",
        "reached-floor",
    ],
)
def test_decide(percent, start, changed, passes, words):
    ok, message = coverage_gate.decide(percent, start, changed)
    assert ok is passes
    assert words in message


def test_an_absolute_filename_resolves_inside_the_repository(tmp_path):
    """Covr writes absolute paths; the one under the repo maps to R/a.R."""
    report = tmp_path / "r.xml"
    report.write_text(
        '<coverage><packages><package><classes><class filename="'
        + (tmp_path / "R" / "a.R").as_posix()
        + '"><lines><line number="1" hits="1"/><line number="2" hits="0"/>'
        "</lines></class></classes></package></packages></coverage>"
    )
    lines = coverage_gate.load_lines(tmp_path, [report])
    assert lines == {"R/a.R": {1: 1, 2: 0}}

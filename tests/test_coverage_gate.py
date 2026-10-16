"""Coverage reports and reviewed repository targets determine gate outcomes.

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
    ("value", "targets", "changed", "passes"),
    [
        (0, {}, (0, 10), True),
        (74.9, {}, None, True),
        (51, {"floor_percent": 52}, None, False),
        (52, {"floor_percent": 52}, None, True),
        (99, {"changed_lines_percent": 80}, (7, 10), False),
        (40, {"changed_lines_percent": 80}, (8, 10), True),
        (40, {"changed_lines_percent": 80}, (0, 0), True),
        (40, {"changed_lines_percent": 80}, None, True),
        (79.99, {"floor_percent": 80}, None, False),
    ],
)
def test_decide(value, targets, changed, passes):
    """Targets use exact percentages; 7/10 fails 80%, while 8/10 passes."""
    ok, message = coverage_gate.decide(value, targets, changed)
    assert ok is passes
    assert "Coverage" in message or "changed lines" in message


def write_policy(tmp_path, text):
    folder = tmp_path / "overrides" / "example"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "coverage.yaml").write_text(text)


def test_default_reports_without_a_numeric_gate(tmp_path):
    targets = coverage_gate.policy(tmp_path, "org/example")
    assert targets == {"floor_percent": None, "changed_lines_percent": None}
    assert "reporting only" in coverage_gate.decide(0, targets, None)[1]


def test_repository_targets_override_reporting_defaults(tmp_path):
    write_policy(
        tmp_path,
        "floor_percent: 60\nchanged_lines_percent: 85\n"
        "rationale: Preserve tested data export paths.\n",
    )
    targets = coverage_gate.policy(tmp_path, "org/example")
    assert not coverage_gate.decide(59, targets, (9, 10))[0]
    assert not coverage_gate.decide(60, targets, (8, 10))[0]
    assert coverage_gate.decide(60, targets, (9, 10))[0]


def test_legacy_baseline_retains_its_floor_without_a_changed_line_default(
    tmp_path,
):
    write_policy(tmp_path, "start_percent: 52\nmeasured_at_commit: abc123\n")
    targets = coverage_gate.policy(tmp_path, "org/example")
    assert not coverage_gate.decide(51, targets, (10, 10))[0]
    assert coverage_gate.decide(52, targets, (0, 10))[0]


@pytest.mark.parametrize(
    "text",
    [
        "floor_percent: 60",  # rationale required for new targets
        "floor_percent: true\nrationale: example",
        "floor_percent: .nan\nrationale: example",
        "floor_percent: .inf\nrationale: example",
        "floor_percent: -1\nrationale: example",
        "changed_lines_percent: 101\nrationale: example",
        "floor_percent: '60'\nrationale: example",
        "floor_percnt: 60\nrationale: example",
        "start_percent: 52",
        "start_percent: 52\nfloor_percent: 60\nmeasured_at_commit: abc123",
        "- invalid",
        "",
    ],
)
def test_invalid_policy_fails_instead_of_disabling_targets(tmp_path, text):
    write_policy(tmp_path, text)
    with pytest.raises(SystemExit):
        coverage_gate.policy(tmp_path, "org/example")


@pytest.mark.parametrize("enforce", [False, True])
@pytest.mark.parametrize("report_kind", ["missing", "empty", "measured"])
def test_cli_enforces_targets_and_requires_measurements(
    tmp_path, enforce, report_kind
):
    if enforce:
        write_policy(
            tmp_path, "floor_percent: 70\nrationale: Data integrity.\n"
        )
    report = tmp_path / "coverage.xml"
    if report_kind == "empty":
        report.write_text("<coverage/>")
    elif report_kind == "measured":
        report.write_text(REPORT.format(root=tmp_path.as_posix()))
    # The planted report covers 4/6 lines, below this project's 70% target.
    result = coverage_gate.main(
        [
            "--report",
            str(report),
            "--repo-dir",
            str(tmp_path),
            "--standards-root",
            str(tmp_path),
            "--repo",
            "org/example",
        ]
    )
    assert result == (1 if enforce else 0)


def test_invalid_policy_is_checked_even_without_a_report(tmp_path):
    write_policy(tmp_path, "floor_percent: 70")
    with pytest.raises(SystemExit):
        coverage_gate.main(
            [
                "--report",
                str(tmp_path / "missing.xml"),
                "--standards-root",
                str(tmp_path),
                "--repo",
                "org/example",
            ]
        )


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


@pytest.mark.parametrize(("line", "expected"), [(2, 1), (3, 0)])
def test_cli_uses_changed_line_measurements(
    tmp_path, monkeypatch, line, expected
):
    write_policy(
        tmp_path,
        "changed_lines_percent: 80\nrationale: Validate changed imports.\n",
    )
    report = tmp_path / "coverage.xml"
    report.write_text(REPORT.format(root=tmp_path.as_posix()))
    # Line 2 has no hits; line 3 has two hits, giving 0% and 100% respectively.
    monkeypatch.setattr(
        coverage_gate.rules_check,
        "parse_diff",
        lambda *_args: {"src/pkg/a.py": {"added": [(line, "value = 1")]}},
    )
    assert (
        coverage_gate.main(
            [
                "--report",
                str(report),
                "--repo-dir",
                str(tmp_path),
                "--standards-root",
                str(tmp_path),
                "--repo",
                "org/example",
                "--base",
                "base",
                "--head",
                "head",
            ]
        )
        == expected
    )


def test_null_legacy_baseline_is_rejected(tmp_path):
    write_policy(tmp_path, "start_percent: null\nmeasured_at_commit: abc123\n")
    with pytest.raises(SystemExit, match="numeric value"):
        coverage_gate.policy(tmp_path, "org/example")

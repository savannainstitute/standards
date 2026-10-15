"""Prose warnings preserve identifiers and source quotations."""

import pytest

from standards import rules_check


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Analyse the colour measurements.", True),
        ("Analyze the color measurements.", False),
        ("Use `colour` as the external field name.", False),
        ('> "Analyse the colour measurements."', False),
        ("Use `colour` to analyse the measurements.", True),
        ("```python\ncolour = 'colour'\n```", False),
    ],
)
def test_literal_exclusions_do_not_hide_surrounding_prose(text, expected):
    """The mixed identifier/prose case must still report the prose word."""
    report = rules_check.Report()
    rules_check.check_markdown_file(report, ".", "README.md", text)
    found = [f for f in report.findings if f.rule == "british-spelling"]
    assert bool(found) == expected
    assert all(not finding.blocks for finding in found)

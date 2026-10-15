"""Bold is reported in prose and left alone inside inline code."""

from standards import rules_check


def findings(text):
    report = rules_check.Report()
    rules_check.check_markdown_file(report, ".", "README.md", text)
    return [(f.rule, f.line, f.message) for f in report.findings]


def test_a_dunder_name_in_backticks_is_not_bold():
    """`__init__.py` and `__main__.py` are file names, not emphasis."""
    text = "- `src/pkg/__main__.py` is the command; `__init__.py` too.\n"
    assert not [f for f in findings(text) if f[0] == "typography"]


def test_bold_in_prose_is_reported():
    """Two asterisks around a word are emphasis."""
    text = "This is **important** to read.\n"
    assert [(f[0], f[1]) for f in findings(text)] == [("typography", 1)]

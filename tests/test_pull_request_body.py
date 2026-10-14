"""The pull request rules read what the author wrote under each heading.

The organization's pull request template puts every heading in every body,
with the guidance in HTML comments. A heading with nothing written under it
is an empty section, and a comment is never an answer.
"""

from test_rules_check import build

from standards import rules_check

TEMPLATE = "\n".join(
    [
        "<!-- Say what the change does and why. -->",
        "",
        "Dependencies:",
        "<!-- Each package this pull request adds, and what it is for. -->",
        "",
        "## Docs added",
        "<!-- Each new Markdown file outside docs/, and why it exists. -->",
        "",
        "## Tests removed or skipped",
        "<!-- Each test removed or skipped, and the reason. -->",
        "",
        "<!-- A change under src/ with no test needs a line starting",
        '"No test because". -->',
        "",
    ]
)

ENVIRONMENT = "\n".join(
    ["name: pipeline", "dependencies:", "  - python=3.13", "  - pip", ""]
)


def scenario(pr_body, base, head):
    return {
        "base": base,
        "head": head,
        "commit_message": "Change",
        "pr_body": pr_body,
    }


def findings(tmp_path, pr_body, base, head):
    repo = tmp_path / "repo"
    repo.mkdir()
    base_sha, head_sha, body = build(repo, scenario(pr_body, base, head))
    found = rules_check.run(
        repo, base_sha, head_sha, body.read_text(encoding="utf-8")
    )
    return {(f.rule, f.path) for f in found}


def test_empty_template_sections_are_empty(tmp_path):
    """Nothing under the headings: every pull request rule still fires."""
    base = {
        "tests/test_a.py": "def test_a():\n    assert 1 == 1\n",
        "tests/test_b.py": "def test_b():\n    assert 2 == 2\n",
        "src/a.py": "X = 1\n",
    }
    head = {
        "tests/test_b.py": base["tests/test_b.py"],
        "src/a.py": "X = 2\n",
        "environment.yml": ENVIRONMENT,
        "method-outline.md": "# Method\n",
    }
    found = findings(tmp_path, TEMPLATE, base, head)
    assert ("dependency-added", "environment.yml") in found
    assert ("test-removed", "tests/test_a.py") in found
    assert ("fix-without-test", "src/a.py") in found
    assert ("stray-markdown", "method-outline.md") in found


def test_filled_template_sections_answer_the_rules(tmp_path):
    """What the author wrote under each heading satisfies its rule."""
    base = {
        "tests/test_a.py": "def test_a():\n    assert 1 == 1\n",
        "tests/test_b.py": "def test_b():\n    assert 2 == 2\n",
        "src/a.py": "X = 1\n",
    }
    head = {
        "tests/test_b.py": base["tests/test_b.py"],
        "src/a.py": "X = 2\n",
        "environment.yml": ENVIRONMENT,
        "method-outline.md": "# Method\n",
    }
    body = TEMPLATE.replace(
        "Dependencies:\n",
        "Dependencies: python, the interpreter; pip, to install the rest\n",
    )
    body = body.replace(
        "## Docs added\n",
        "## Docs added\nmethod-outline.md, the method in prose\n",
    )
    body = body.replace(
        "## Tests removed or skipped\n",
        "## Tests removed or skipped\ntest_a tested the old constant\n",
    )
    body += "No test because the constant is read by the existing test.\n"
    found = findings(tmp_path, body, base, head)
    assert not {
        rule
        for rule, _ in found
        if rule
        in (
            "dependency-added",
            "test-removed",
            "fix-without-test",
            "stray-markdown",
        )
    }


def test_a_package_name_inside_another_word_is_not_named(tmp_path):
    """The word pipeline does not name the package pip."""
    base = {"README.md": "# Pipeline\n"}
    head = {"README.md": base["README.md"], "environment.yml": ENVIRONMENT}
    body = "Dependencies: python, and the pipeline template's packages\n"
    found = findings(tmp_path, body, base, head)
    assert ("dependency-added", "environment.yml") in found


def test_section_ends_at_the_next_heading():
    """Text under a later heading is not part of the earlier section."""
    body = "## Docs added\nfirst\n\n## Tests removed or skipped\nsecond\n"
    assert rules_check.body_section(body, "Docs added").strip() == "first"
    assert (
        rules_check.body_section(body, "Tests removed or skipped").strip()
        == "second"
    )
    assert rules_check.body_section(body, "Dependencies") == ""

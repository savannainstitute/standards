"""Only a manifest's dependency entries are read as dependencies."""

from standards import rules_check

PACKAGE_JSON = "\n".join(
    [
        "{",
        '  "name": "app",',
        '  "version": "1.0.0",',
        '  "scripts": {',
        '    "build": "vite build"',
        "  },",
        '  "devDependencies": {',
        '    "vite": "8.3.4"',
        "  }",
        "}",
    ]
)

DESCRIPTION = "\n".join(
    [
        "Package: packagename",
        "Version: 0.1.0",
        "Authors@R: c(",
        '    person("First", "Last", email = "first.last@example.org",',
        '           role = c("aut", "cre"))',
        "  )",
        "License: MIT + file LICENSE",
        "Imports:",
        "    dplyr (>= 1.1.0),",
        "    tidyr",
        "Suggests:",
        "    testthat",
    ]
)


def every_line_added(text):
    return list(enumerate(text.splitlines(), 1))


def test_package_json_version_is_not_a_dependency():
    """Line 8 is the one entry under devDependencies; line 3 is the version."""
    found = rules_check.dependency_names(
        "package.json", every_line_added(PACKAGE_JSON), PACKAGE_JSON
    )
    assert found == [(8, "vite")]


def test_description_reads_only_the_dependency_fields():
    """Lines 9, 10 and 12 sit under Imports and Suggests; 4 and 5 do not."""
    found = rules_check.dependency_names(
        "DESCRIPTION", every_line_added(DESCRIPTION), DESCRIPTION
    )
    assert found == [(9, "dplyr"), (10, "tidyr"), (12, "testthat")]

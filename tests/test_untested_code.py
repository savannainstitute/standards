"""A code file that defines functions has its own test file.

Each case plants a small repository and states by hand which files the rule
names. A file that defines no function or class has nothing to unit-test and
is never named; a repository with code and no test file at all is named once.
"""

import pytest

from standards import rules_check

PY_FUNCTION = "def area(width, height):\n    return width * height\n"
PY_SCRIPT = "print(1 + 1)\n"
R_FUNCTION = "area <- function(width, height) {\n  width * height\n}\n"
TS_FUNCTION = (
    "export function area(w: number, h: number) {\n  return w * h;\n}\n"
)
TS_ARROW = "export const area = (w: number, h: number) => w * h;\n"
TEST_BODY = "def test_x():\n    assert 2 * 3 == 6\n"


def findings(tmp_path, tree):
    for path, text in tree.items():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    paths = sorted(tree)
    return sorted(rules_check.untested_code(tmp_path, paths))


@pytest.mark.parametrize(
    ("tree", "expected"),
    [
        (
            {
                "src/pkg/geometry.py": PY_FUNCTION,
                "tests/test_geometry.py": TEST_BODY,
            },
            [],
        ),
        (
            {
                "src/pkg/geometry.py": PY_FUNCTION,
                "src/pkg/units.py": PY_FUNCTION,
                "tests/test_geometry.py": TEST_BODY,
            },
            [("src/pkg/units.py", "tests/test_units.py")],
        ),
        (
            {
                "R/area.R": R_FUNCTION,
                "R/volume.R": R_FUNCTION,
                "tests/testthat/test-area.R": "test_that('x', {})\n",
            },
            [("R/volume.R", "tests/testthat/test-volume.R")],
        ),
        (
            {
                "src/area.ts": TS_FUNCTION,
                "src/volume.ts": TS_ARROW,
                "tests/area.test.ts": "it('x', () => {});\n",
            },
            [("src/volume.ts", "tests/volume.test.ts")],
        ),
        (
            {
                "src/pkg/__init__.py": PY_FUNCTION,
                "src/pkg/geometry.py": PY_FUNCTION,
                "tests/conftest.py": PY_FUNCTION,
                "tests/test_geometry_area.py": TEST_BODY,
                ".claude/hooks/hook.py": PY_FUNCTION,
                "docs/example.py": PY_FUNCTION,
                "vite.config.ts": TS_FUNCTION,
            },
            [],
        ),
    ],
    ids=["tested", "one-untested", "r", "typescript", "exempt-places"],
)
def test_each_untested_file_is_named(tmp_path, tree, expected):
    assert findings(tmp_path, tree) == expected


def test_scripts_with_no_tests_at_all_are_named_once(tmp_path):
    """Two scripts define nothing, but the repository has no test file."""
    tree = {"run.py": PY_SCRIPT, "scripts/01_clean.R": "x <- 1\n"}
    assert findings(tmp_path, tree) == [("", "tests/")]


def test_scripts_beside_a_test_file_are_not_named(tmp_path):
    tree = {"run.py": PY_SCRIPT, "tests/test_run.py": TEST_BODY}
    assert findings(tmp_path, tree) == []

"""The rule list: one entry per check the slop check performs.

This module is the single source of the rule ids, their severity and their
wording. The rendered list in docs/RULES.md is generated from it, and the slop
check reports findings by these ids. A rule that blocks fails the check; a
rule that warns is printed and does not fail it. The examples are the shapes
the check looks for; they are rendered inside a code block so that the
rendered list does not trip the check itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """One check: id, severity, where it looks, what it asks, how to fix it."""

    id: str
    blocks: bool
    scope: str
    rule: str
    fix: str
    examples: tuple = ()


TREE = "every tracked file"
CODE = "code files"
PROSE = "comments, docstrings and Markdown"
PATHS = "file paths"
DIFF = "the pull request's changes"
TEXT = "commit messages and the pull request text"

RULES = (
    Rule(
        "contrast",
        False,
        PROSE + ", " + TEXT,
        "No contrast constructions used for effect.",
        "State the point directly; drop the half of the sentence that names "
        "what it is not.",
        (
            "not X, but Y",
            "isn't X, it's Y",
            "it's X, never Y",
            "this is X, not Y",
        ),
    ),
    Rule(
        "narration",
        False,
        "comments, " + TEXT,
        "A comment states a constraint or an invariant; it does not narrate "
        "the change or the conversation.",
        "Delete the comment, or rewrite it to say what the code must hold "
        "true.",
        (
            "now we handle",
            "updated to fix",
            "as requested",
            "changed this to",
            "per your feedback",
        ),
    ),
    Rule(
        "banner",
        False,
        CODE,
        "No comment block of three or more consecutive comment lines, and no "
        "divider line of dashes, equals signs or asterisks. Configuration "
        "files, roxygen comments and block comments in the slash languages "
        "are exempt.",
        "Keep one line that states the constraint; move anything longer to "
        "the docstring or docs/.",
    ),
    Rule(
        "docstring-history",
        False,
        "comments and docstrings",
        "A docstring or comment states purpose, not history: no dates and no "
        "account of what the code did before.",
        "Git history is the record; remove the history from the docstring.",
        ("2023-04-01", "originally", "historically", "because the previous"),
    ),
    Rule(
        "decision-attribution",
        False,
        "comments, docstrings, Markdown, configuration files, " + TEXT,
        "A file states what holds, not who decided it or when: no person "
        "and date in parentheses, no decision credited to a person or a "
        "date, no line saying what a person asked for or wants.",
        "State the decision itself. The pull request and git history "
        "record who made it and when.",
        (
            "(Name, 2026-10-12)",
            "approved by Name",
            "decided on 2026-10-12",
            "Name asked that",
            "per Name's request",
        ),
    ),
    Rule(
        "chat-residue",
        True,
        CODE,
        "No chat left in source: Markdown fences, phrases from a "
        "conversation, placeholder comments standing in for code, or a "
        "function body that only raises NotImplementedError.",
        "Finish the code or remove the stub.",
        (
            "here is the updated code",
            "rest of the code unchanged",
            "... existing code",
            "TODO: implement",
            'stop("not implemented")',
        ),
    ),
    Rule(
        "typography",
        False,
        TREE,
        "No em dashes or emoji anywhere; no bold in Markdown; "
        "none of the words below written in capitals for emphasis in a "
        "comment or Markdown. A capitalized identifier or acronym is fine.",
        "Use a comma, a period or a plain word.",
        (
            "NOT",
            "NEVER",
            "ALWAYS",
            "MUST",
            "SHOULD",
            "DO",
            "DONT",
            "IMPORTANT",
            "CRITICAL",
            "WARNING",
            "NOTE",
            "REQUIRED",
            "ONLY",
            "ALL",
            "ANY",
            "EVERY",
        ),
    ),
    Rule(
        "sales-vocabulary",
        False,
        PROSE + ", " + TEXT,
        "No sales vocabulary.",
        "Say what the code does.",
        ("robust", "comprehensive", "seamless", "production-ready"),
    ),
    Rule(
        "scratch-file",
        True,
        PATHS,
        "No scratch or planning files committed: a Markdown or text file "
        "named for a plan, summary, time log, session or notes, or any file "
        "named scratch or scratchpad.",
        "Keep them out of the repo, or move a lasting document under docs/ "
        "with a name that says what it holds.",
        ("notes.md", "PLAN.md", "time_log.md", "scratchpad.py"),
    ),
    Rule(
        "copy-suffix",
        True,
        PATHS,
        "No versions kept as copies: a version, new, final, backup, old or "
        "copy suffix, or a date in a file name. Files under data/ and "
        "raw_data/ are exempt.",
        "Keep one file; git history holds the versions.",
        (
            "analysis_v2.py",
            "model_new.R",
            "report-new.Rmd",
            "run_20221108.R",
            "map_2026-08-24.py",
        ),
    ),
    Rule(
        "machine-file",
        True,
        PATHS,
        "No machine files, caches or build output.",
        "Delete the file and add the pattern to .gitignore if it is missing.",
        (
            ".DS_Store",
            "Thumbs.db",
            ".Rhistory",
            ".RData",
            "__pycache__/",
            "*.pyc",
            "*.egg-info/",
            "node_modules/",
            ".ipynb_checkpoints/",
            "dist/",
            "build/",
            ".vscode/",
            ".Rproj.user/",
        ),
    ),
    Rule(
        "notebook-output",
        True,
        "Jupyter notebooks",
        "A committed notebook carries no cell outputs.",
        "Clear outputs before committing; the pre-commit hook does it.",
    ),
    Rule(
        "silent-default",
        False,
        CODE,
        "A required input has no silent default; the shapes below are "
        "reported for review.",
        "Raise or stop when the input is missing, or state why the default "
        "is correct.",
        (
            '.get(key, None)',
            '.get(key, "")',
            "x %||% y",
            "ifelse(is.na(x), 0, x)",
            "x ?? null",
        ),
    ),
    Rule(
        "machine-path",
        True,
        CODE + " and Markdown",
        "No machine-specific paths.",
        "Take the path from an argument, a config file or an environment "
        "variable.",
        ("C:\\Users\\", "/Users/<name>/", "/home/<name>/", "~/Dropbox/"),
    ),
    Rule(
        "silenced-check",
        True,
        CODE,
        "A silenced lint, type or test check names the rule it silences and "
        "the reason, on the same line. The pytest marker needs(\"reason\") "
        "is the way to mark a test the hosted check cannot run.",
        "Fix the finding, or write the rule code and the reason after the "
        "marker.",
        (
            "# noqa",
            "# type: ignore",
            "# nolint",
            "eslint-disable",
            "shellcheck disable",
            "pragma: no cover",
            "@pytest.mark.skip",
            "@pytest.mark.xfail",
        ),
    ),
    Rule(
        "unsourced-constant",
        False,
        CODE,
        "A numeric constant assigned to an upper-case name carries its "
        "source in a comment on the same or the previous line.",
        "Write where the number comes from: a config file, the data, a "
        "paper, a measurement.",
    ),
    Rule(
        "swallowed-error",
        False,
        "R files",
        "An error is not swallowed. Python's equivalents are ruff rules "
        "E722, BLE001, S110 and S112.",
        "Let the error propagate, or handle the one case you expect and say "
        "which.",
        ("tryCatch(..., error = function(e) NULL)", "try(..., silent = TRUE)"),
    ),
    Rule(
        "always-true-test",
        True,
        "test files",
        "No test that cannot fail.",
        "Assert on a value computed from a planted input whose expected "
        "answer is derived in a comment.",
        ("assert True", "expect_true(TRUE)", "expect(true).toBe(true)"),
    ),
    Rule(
        "unverified-citation",
        False,
        TREE,
        "A DOI carries a URL beside it, so the reference was read and can "
        "be followed.",
        "Add the URL you read it from, or remove the citation.",
    ),
    Rule(
        "synthetic-fallback",
        False,
        CODE,
        "No example or synthetic data as a fallback when a file is missing: "
        "a missing-file test beside the words below is reported for review.",
        "Fail when the input is missing. Example data is declared in "
        "data/README.md, never substituted.",
        (
            "sample",
            "example",
            "synthetic",
            "dummy",
            "rnorm",
            "runif",
            "np.random",
        ),
    ),
    Rule(
        "silent-row-drop",
        False,
        CODE,
        "A call that drops or fills missing rows carries a comment on the "
        "same line stating the count or the reason.",
        "Report how many rows are dropped and why, in the comment and in "
        "the output.",
        ("dropna(", "fillna(", "na.omit(", "drop_na(", "filter(!is.na("),
    ),
    Rule(
        "untested-code",
        True,
        CODE,
        "A code file that defines a function or a class has its own test "
        "file, named as the layouts name it: `test_<name>.py`, "
        "`test-<name>.R` or `<name>.test.ts`. A repository with code and no "
        "test file at all fails once. Files that define nothing, such as "
        "scripts that only run steps, need no test file of their own.",
        "Add the test file the finding names, testing what the code file "
        "defines.",
    ),
    Rule(
        "readme-path",
        True,
        "README files and docs/",
        "Every path named in backticks in a README or a docs/ file exists "
        "in the repo.",
        "Fix the path or remove the sentence.",
    ),
    Rule(
        "secret-literal",
        True,
        CODE,
        "A string assigned to a name like password, token, secret or "
        "api_key is not committed unless the line says it is a public "
        "fixture and the repo's entry under overrides/ in the standards "
        "repo cites where it is published.",
        "Read the value from the environment or a file outside the repo. "
        "For a public test fixture, add the comment and the cited allowlist "
        "entry.",
    ),
    Rule(
        "standards-copy",
        True,
        "the files copied from the standards repository",
        "The caller workflow and the files for coding agents match the "
        "standards repository's copies, and the pre-commit hooks are pinned "
        "to a release with the current major version, such as any v1 "
        "release while the standards are at version 1. Text below the "
        "marker line in AGENTS.md and CLAUDE.md belongs to the repository "
        "and is not compared.",
        "Copy the file the finding names from the template for this kind "
        "of project in the standards repository, or set the rev it names.",
    ),
    Rule(
        "stray-markdown",
        True,
        DIFF,
        "A pull request that adds a Markdown file outside docs/, other than "
        "a README.md or the root AGENTS.md, CLAUDE.md, CHANGELOG.md, "
        "NEWS.md, LICENSE.md or HOSTING.md, lists it in the pull request "
        "text under a Docs added heading.",
        "Move the file under docs/, or list it under a Docs added heading "
        "with one line on why it exists.",
    ),
    Rule(
        "dependency-added",
        True,
        DIFF,
        "A pull request that adds a dependency to pyproject.toml, a "
        "requirements file, environment.yml, DESCRIPTION or package.json "
        "names it in the pull request text on a Dependencies: line.",
        "Add a Dependencies: line naming each new package and what it is for.",
    ),
    Rule(
        "test-removed",
        True,
        DIFF,
        "A pull request that removes a test function lists it in the pull "
        "request text under a Tests removed or skipped heading.",
        "Keep the test, or list it under that heading with the reason.",
    ),
    Rule(
        "fix-without-test",
        True,
        DIFF,
        "A pull request that changes source under src/, R/ or packages/ "
        "adds at least one line under tests/, or carries a No test because "
        "line in the pull request text.",
        "Add the test that fails without the change, or write the No test "
        "because line.",
    ),
    Rule(
        "attribution",
        True,
        TEXT,
        "No tool attribution in a commit message or pull request text: no "
        "co-author trailer naming a model vendor, no generated-with line, "
        "no vendor noreply address.",
        "Remove the trailer or line; the committed project settings turn it "
        "off.",
        (
            "Co-authored-by: Claude <noreply@anthropic.com>",
            "Generated with [Claude Code]",
        ),
    ),
)

BY_ID = {rule.id: rule for rule in RULES}

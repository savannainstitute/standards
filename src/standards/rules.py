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
        'State requirements directly. Rhetorical contrast constructions '
        'are flagged for review.',
        'Remove the unnecessary comparison.',
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
        'Comments describe constraints and behavior. Conversational '
        'instructions and accounts of the editing process are flagged.',
        'Replace editing commentary with the relevant technical '
        'information, or remove it.',
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
        'Comment blocks of three or more consecutive lines and decorative '
        'divider lines are flagged. Configuration files, roxygen comments, '
        'and block comments in languages using slash-style comments are '
        'exempt.',
        'Use concise comments; place longer explanations in docstrings or '
        'documentation.',
    ),
    Rule(
        "docstring-history",
        False,
        "comments and docstrings",
        'Dates and change-history language in comments and docstrings are '
        'flagged.',
        'Describe current purpose and behavior. Preserve change history in '
        'commits and pull requests.',
        ("2023-04-01", "originally", "historically", "because the previous"),
    ),
    Rule(
        "decision-attribution",
        True,
        "comments, docstrings, Markdown, configuration files, " + TEXT,
        'Project files describe requirements and decisions without '
        'attributing them to a person or date. Person-and-date '
        'annotations, approval credits, and statements of personal '
        'requests are rejected.',
        'Retain the technical decision; record its authorship and timing '
        'in the pull request or commit history.',
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
        'Source files must contain complete code. Conversation fragments, '
        'Markdown fences, placeholder comments, and function bodies that '
        'only raise NotImplementedError are rejected.',
        'Implement the missing behavior or remove the incomplete code.',
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
        "british-spelling",
        False,
        PROSE + ", " + TEXT,
        'Project prose uses American English. The check excludes code '
        'identifiers and library argument names. Inline backtick literals '
        'and Markdown block quotations are excluded from spelling checks.',
        'Replace flagged spellings with their American English equivalents.',
        ("colour", "behaviour", "analyse", "centre", "labelled", "grey"),
    ),
    Rule(
        "scratch-file",
        True,
        PATHS,
        'Scratch files and temporary planning records must not be '
        'committed. The check identifies Markdown and text filenames '
        'associated with plans, summaries, time logs, sessions, or notes, '
        'and files named scratch or scratchpad.',
        'Keep temporary records outside the repository. Place lasting '
        'documentation under docs/ with a descriptive filename.',
        ("notes.md", "PLAN.md", "time_log.md", "scratchpad.py"),
    ),
    Rule(
        "copy-suffix",
        True,
        PATHS,
        'Version, new, final, backup, old, copy, and date suffixes in '
        'filenames are rejected. Files under data/ and raw_data/ are '
        'exempt.',
        'Maintain one current file and use Git history for earlier versions.',
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
        'Machine-specific files, caches, and build outputs must not be '
        'committed.',
        'Remove the tracked file and add its pattern to .gitignore where '
        'needed.',
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
        'Committed Jupyter notebooks must have empty cell outputs.',
        'Clear outputs before committing; the configured pre-commit hook '
        'performs this step.',
    ),
    Rule(
        "silent-default",
        False,
        CODE,
        'Fallback values for required inputs are flagged for review.',
        'Raise an error when required input is absent, or document why the '
        'default is valid.',
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
        'Paths tied to an individual machine or user account are prohibited.',
        'Supply paths through arguments, configuration, or environment '
        'variables.',
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
            "# hadolint ignore=DL3008",
            'it.skip("a test name"',
        ),
    ),
    Rule(
        "unsourced-constant",
        False,
        CODE,
        'A numeric constant assigned to an uppercase name requires a '
        'source comment on the same or preceding line.',
        'Identify the configuration, dataset, publication, or measurement '
        'that supplies the value.',
    ),
    Rule(
        "swallowed-error",
        False,
        "R files",
        'R error handlers that discard failures are flagged. Python '
        'equivalents are checked by Ruff rules E722, BLE001, S110, and '
        'S112.',
        'Propagate the error or explicitly handle and document the '
        'expected failure condition.',
        ("tryCatch(..., error = function(e) NULL)", "try(..., silent = TRUE)"),
    ),
    Rule(
        "always-true-test",
        True,
        "test files",
        'Tests must include assertions capable of failing when behavior is '
        'incorrect. Unconditionally true assertions are rejected.',
        'Use a controlled input and document how the expected result was '
        'independently derived.',
        ("assert True", "expect_true(TRUE)", "expect(true).toBe(true)"),
    ),
    Rule(
        "unverified-citation",
        False,
        TREE,
        'A DOI requires an accompanying source URL.',
        'Provide the URL used to verify the reference. A URL makes the '
        'reference traceable; the automated check cannot establish that it '
        'was read.',
    ),
    Rule(
        "synthetic-fallback",
        False,
        CODE,
        'Substitution of example or synthetic data when an input file is '
        'missing is flagged for review.',
        'Fail explicitly for missing required inputs. Identify intentional '
        'example datasets in data/README.md.',
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
        'Calls that drop or fill missing rows require a same-line comment '
        'stating the count or reason.',
        'Document the treatment of missing values and report affected row '
        'counts in the output.',
        ("dropna(", "fillna(", "na.omit(", "drop_na(", "filter(!is.na("),
    ),
    Rule(
        "untested-code",
        True,
        CODE,
        'Each source file defining a function or class requires a '
        'corresponding test file: `test_<name>.py`, `test-<name>.R`, or '
        '`<name>.test.ts`. Repositories containing code require at least '
        'one test file. Scripts defining no functions or classes do not '
        'require an individual test file.',
        'Add the indicated test file and test the behavior defined by the '
        'source file.',
    ),
    Rule(
        "readme-path",
        True,
        "README files and docs/",
        'Repository paths in inline code in README files and docs/ must '
        'resolve to existing files or directories.',
        'Correct the path or remove the invalid reference.',
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
        'The caller workflow and local hooks must reference the same full '
        'commit SHA. Shared coding-agent files must match that release. '
        'The hosted check verifies the executing workflow revision. '
        'Repository-specific text below the '
        'marker in AGENTS.md and CLAUDE.md is excluded from comparison. '
        'This comparison runs on pull requests; local hooks use their '
        'pinned version.',
        'Use standards-adopt with the selected release commit to update '
        'the workflow, local hooks, and agent files together.',
    ),
    Rule(
        "stray-markdown",
        True,
        DIFF,
        'New Markdown files outside docs/ must be listed under a Docs '
        'added heading in the pull request description. README.md files '
        'and root AGENTS.md, CLAUDE.md, CHANGELOG.md, NEWS.md, LICENSE.md, '
        'and HOSTING.md are exempt.',
        'Place the document under docs/ or list its filename and purpose '
        'under that heading.',
    ),
    Rule(
        "dependency-added",
        True,
        DIFF,
        'Dependencies added to pyproject.toml, requirements files, '
        'environment.yml, DESCRIPTION, or package.json must be identified '
        'on a Dependencies: line in the pull request description.',
        'List each added package and its purpose.',
    ),
    Rule(
        "test-removed",
        True,
        DIFF,
        'Removed test functions must be identified under a Tests removed '
        'or skipped heading in the pull request description.',
        'List each removed test and the reason, or retain the test.',
    ),
    Rule(
        "fix-without-test",
        True,
        DIFF,
        'Changes to source under src/, R/, or packages/ must include at '
        'least one added line under tests/ or a No test because line in '
        'the pull request description.',
        'Add a regression test that fails without the change, or explain '
        'why a test change is unnecessary.',
    ),
    Rule(
        "attribution",
        True,
        TEXT,
        'Commit messages and pull request descriptions must omit '
        'coding-tool attribution, including model-vendor co-author '
        'trailers, generated-with statements, and vendor noreply '
        'addresses.',
        'Remove the attribution and use the repository settings that '
        'disable automatic tool credits.',
        (
            "Co-authored-by: Claude <noreply@anthropic.com>",
            "Generated with [Claude Code]",
        ),
    ),
    Rule(
        "installer-committed",
        True,
        PATHS,
        'Third-party software distributions, including wheels, '
        'executables, and installers, must not be committed.',
        'Remove the distribution and document installation in the README '
        'or environment specification.',
        ("metashape.whl", "setup.exe", "tool.msi", "app.dmg", "lib.deb"),
    ),
    Rule(
        "binary-outside-lfs",
        True,
        DIFF,
        "A pull request that adds a binary file (an image, raster, point "
        "cloud, video, model, archive, PDF, spreadsheet or R data file; "
        "SVG is text) adds it through Git LFS: the path matches a "
        "filter=lfs line in .gitattributes and the committed file is the "
        "LFS pointer.",
        "Run git lfs install once, add the pattern to .gitattributes with "
        "git lfs track, and commit the file again. A large or growing "
        "collection belongs in object storage, named in data/README.md.",
    ),
    Rule(
        "data-unlisted",
        False,
        "files under data/",
        'Each file under data/ must be listed in data/README.md with its '
        'source, date, license, units, and input or output status.',
        'Add the missing entry or move a file that does not belong in data/.',
    ),
)

BY_ID = {rule.id: rule for rule in RULES}

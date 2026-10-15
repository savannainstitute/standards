# The rules

Every repository in the organization is checked against this list on every pull request. A rule that
blocks fails the check, and the pull request cannot merge until it passes. A rule that warns prints
its finding for the author and the reviewer and does not fail the check.

This file is generated from the rule list in `src/standards/rules.py`; edit that file and run
`render-rules`.

## contrast

Warns. Looks at comments, docstrings and Markdown, commit messages and the pull request text.

No contrast constructions used for effect.

To fix it: State the point directly; drop the half of the sentence that names what it is not.

Shapes the check looks for:

```text
not X, but Y
isn't X, it's Y
it's X, never Y
this is X, not Y
```

## narration

Warns. Looks at comments, commit messages and the pull request text.

A comment states a constraint or an invariant; it does not narrate the change or the conversation.

To fix it: Delete the comment, or rewrite it to say what the code must hold true.

Shapes the check looks for:

```text
now we handle
updated to fix
as requested
changed this to
per your feedback
```

## banner

Warns. Looks at code files.

No comment block of three or more consecutive comment lines, and no divider line of dashes, equals
signs or asterisks. Configuration files, roxygen comments and block comments in the slash languages
are exempt.

To fix it: Keep one line that states the constraint; move anything longer to the docstring or docs/.

## docstring-history

Warns. Looks at comments and docstrings.

A docstring or comment states purpose, not history: no dates and no account of what the code did
before.

To fix it: Git history is the record; remove the history from the docstring.

Shapes the check looks for:

```text
2023-04-01
originally
historically
because the previous
```

## decision-attribution

Blocks. Looks at comments, docstrings, Markdown, configuration files, commit messages and the pull
request text.

A file states what holds, not who decided it or when: no person and date in parentheses, no decision
credited to a person or a date, no line saying what a person asked for or wants.

To fix it: State the decision itself. The pull request and git history record who made it and when.

Shapes the check looks for:

```text
(Name, 2026-10-12)
approved by Name
decided on 2026-10-12
Name asked that
per Name's request
```

## chat-residue

Blocks. Looks at code files.

No chat left in source: Markdown fences, phrases from a conversation, placeholder comments standing
in for code, or a function body that only raises NotImplementedError.

To fix it: Finish the code or remove the stub.

Shapes the check looks for:

```text
here is the updated code
rest of the code unchanged
... existing code
TODO: implement
stop("not implemented")
```

## typography

Warns. Looks at every tracked file.

No em dashes or emoji anywhere; no bold in Markdown; none of the words below written in capitals for
emphasis in a comment or Markdown. A capitalized identifier or acronym is fine.

To fix it: Use a comma, a period or a plain word.

Shapes the check looks for:

```text
NOT
NEVER
ALWAYS
MUST
SHOULD
DO
DONT
IMPORTANT
CRITICAL
WARNING
NOTE
REQUIRED
ONLY
ALL
ANY
EVERY
```

## sales-vocabulary

Warns. Looks at comments, docstrings and Markdown, commit messages and the pull request text.

No sales vocabulary.

To fix it: Say what the code does.

Shapes the check looks for:

```text
robust
comprehensive
seamless
production-ready
```

## scratch-file

Blocks. Looks at file paths.

No scratch or planning files committed: a Markdown or text file named for a plan, summary, time log,
session or notes, or any file named scratch or scratchpad.

To fix it: Keep them out of the repo, or move a lasting document under docs/ with a name that says
what it holds.

Shapes the check looks for:

```text
notes.md
PLAN.md
time_log.md
scratchpad.py
```

## copy-suffix

Blocks. Looks at file paths.

No versions kept as copies: a version, new, final, backup, old or copy suffix, or a date in a file
name. Files under data/ and raw_data/ are exempt.

To fix it: Keep one file; git history holds the versions.

Shapes the check looks for:

```text
analysis_v2.py
model_new.R
report-new.Rmd
run_20221108.R
map_2026-08-24.py
```

## machine-file

Blocks. Looks at file paths.

No machine files, caches or build output.

To fix it: Delete the file and add the pattern to .gitignore if it is missing.

Shapes the check looks for:

```text
.DS_Store
Thumbs.db
.Rhistory
.RData
__pycache__/
*.pyc
*.egg-info/
node_modules/
.ipynb_checkpoints/
dist/
build/
.vscode/
.Rproj.user/
```

## notebook-output

Blocks. Looks at Jupyter notebooks.

A committed notebook carries no cell outputs.

To fix it: Clear outputs before committing; the pre-commit hook does it.

## silent-default

Warns. Looks at code files.

A required input has no silent default; the shapes below are reported for review.

To fix it: Raise or stop when the input is missing, or state why the default is correct.

Shapes the check looks for:

```text
.get(key, None)
.get(key, "")
x %||% y
ifelse(is.na(x), 0, x)
x ?? null
```

## machine-path

Blocks. Looks at code files and Markdown.

No machine-specific paths.

To fix it: Take the path from an argument, a config file or an environment variable.

Shapes the check looks for:

```text
C:\Users\
/Users/<name>/
/home/<name>/
~/Dropbox/
```

## silenced-check

Blocks. Looks at code files.

A silenced lint, type or test check names the rule it silences and the reason, on the same line. The
pytest marker needs("reason") is the way to mark a test the hosted check cannot run.

To fix it: Fix the finding, or write the rule code and the reason after the marker.

Shapes the check looks for:

```text
# noqa
# type: ignore
# nolint
eslint-disable
shellcheck disable
pragma: no cover
@pytest.mark.skip
@pytest.mark.xfail
```

## unsourced-constant

Warns. Looks at code files.

A numeric constant assigned to an upper-case name carries its source in a comment on the same or the
previous line.

To fix it: Write where the number comes from: a config file, the data, a paper, a measurement.

## swallowed-error

Warns. Looks at R files.

An error is not swallowed. Python's equivalents are ruff rules E722, BLE001, S110 and S112.

To fix it: Let the error propagate, or handle the one case you expect and say which.

Shapes the check looks for:

```text
tryCatch(..., error = function(e) NULL)
try(..., silent = TRUE)
```

## always-true-test

Blocks. Looks at test files.

No test that cannot fail.

To fix it: Assert on a value computed from a planted input whose expected answer is derived in a
comment.

Shapes the check looks for:

```text
assert True
expect_true(TRUE)
expect(true).toBe(true)
```

## unverified-citation

Warns. Looks at every tracked file.

A DOI carries a URL beside it, so the reference was read and can be followed.

To fix it: Add the URL you read it from, or remove the citation.

## synthetic-fallback

Warns. Looks at code files.

No example or synthetic data as a fallback when a file is missing: a missing-file test beside the
words below is reported for review.

To fix it: Fail when the input is missing. Example data is declared in data/README.md, never
substituted.

Shapes the check looks for:

```text
sample
example
synthetic
dummy
rnorm
runif
np.random
```

## silent-row-drop

Warns. Looks at code files.

A call that drops or fills missing rows carries a comment on the same line stating the count or the
reason.

To fix it: Report how many rows are dropped and why, in the comment and in the output.

Shapes the check looks for:

```text
dropna(
fillna(
na.omit(
drop_na(
filter(!is.na(
```

## untested-code

Blocks. Looks at code files.

A code file that defines a function or a class has its own test file, named as the layouts name it:
`test_<name>.py`, `test-<name>.R` or `<name>.test.ts`. A repository with code and no test file at
all fails once. Files that define nothing, such as scripts that only run steps, need no test file of
their own.

To fix it: Add the test file the finding names, testing what the code file defines.

## readme-path

Blocks. Looks at README files and docs/.

Every path named in backticks in a README or a docs/ file exists in the repo.

To fix it: Fix the path or remove the sentence.

## secret-literal

Blocks. Looks at code files.

A string assigned to a name like password, token, secret or api_key is not committed unless the line
says it is a public fixture and the repo's entry under overrides/ in the standards repo cites where
it is published.

To fix it: Read the value from the environment or a file outside the repo. For a public test
fixture, add the comment and the cited allowlist entry.

## standards-copy

Blocks. Looks at the files copied from the standards repository.

The caller workflow and the files for coding agents match the standards repository's copies, and
.pre-commit-config.yaml runs the standards hooks at any commit. Text below the marker line in
AGENTS.md and CLAUDE.md belongs to the repository and is not compared. Checked on the pull request
only, since pre-commit runs the commit the repository pins.

To fix it: Copy the file the finding names from the template for this kind of project in the
standards repository. To run newer hooks on your computer, run pre-commit autoupdate.

## stray-markdown

Blocks. Looks at the pull request's changes.

A pull request that adds a Markdown file outside docs/, other than a README.md or the root
AGENTS.md, CLAUDE.md, CHANGELOG.md, NEWS.md, LICENSE.md or HOSTING.md, lists it in the pull request
text under a Docs added heading.

To fix it: Move the file under docs/, or list it under a Docs added heading with one line on why it
exists.

## dependency-added

Blocks. Looks at the pull request's changes.

A pull request that adds a dependency to pyproject.toml, a requirements file, environment.yml,
DESCRIPTION or package.json names it in the pull request text on a Dependencies: line.

To fix it: Add a Dependencies: line naming each new package and what it is for.

## test-removed

Blocks. Looks at the pull request's changes.

A pull request that removes a test function lists it in the pull request text under a Tests removed
or skipped heading.

To fix it: Keep the test, or list it under that heading with the reason.

## fix-without-test

Blocks. Looks at the pull request's changes.

A pull request that changes source under src/, R/ or packages/ adds at least one line under tests/,
or carries a No test because line in the pull request text.

To fix it: Add the test that fails without the change, or write the No test because line.

## attribution

Blocks. Looks at commit messages and the pull request text.

No tool attribution in a commit message or pull request text: no co-author trailer naming a model
vendor, no generated-with line, no vendor noreply address.

To fix it: Remove the trailer or line; the committed project settings turn it off.

Shapes the check looks for:

```text
Co-authored-by: Claude <noreply@anthropic.com>
Generated with [Claude Code]
```

## installer-committed

Blocks. Looks at file paths.

Someone else's software is never committed: no wheel, executable or installer.

To fix it: Delete the file; the README or the environment file says where to get the program.

Shapes the check looks for:

```text
metashape.whl
setup.exe
tool.msi
app.dmg
lib.deb
```

## binary-outside-lfs

Blocks. Looks at the pull request's changes.

A pull request that adds a binary file (an image, raster, point cloud, video, model, archive, PDF,
spreadsheet or R data file; SVG is text) adds it through Git LFS: the path matches a filter=lfs line
in .gitattributes and the committed file is the LFS pointer.

To fix it: Run git lfs install once, add the pattern to .gitattributes with git lfs track, and
commit the file again. A large or growing collection belongs in object storage, named in
data/README.md.

## data-unlisted

Warns. Looks at files under data/.

Every file under data/ is named in data/README.md, which gives its source, date, license and units
and says whether it is an input or an output.

To fix it: Add a line for the file to data/README.md, or move the file.

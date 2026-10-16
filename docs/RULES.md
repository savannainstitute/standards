# Automated check reference

This reference documents the organization-specific automated checks proposed for Savanna Institute
repositories. Initial feedback is due November 13, 2026. Staged migration begins December 4, 2026;
all active organization repositories must comply with the standards by March 5, 2027. Feedback
continues during migration and afterward.

Under the proposed migration process, required checks are activated with each owner during
migration, after the setup is verified. Each repository is checked in full after its initial
cleanup; rules identified as change-specific inspect the pull request's changes. The same
requirements apply to all authors, including work produced with coding agents.

Blocking findings fail the check and prevent merging. Advisory findings are warnings for review and
do not fail the check. Each entry gives the rule ID reported in the log, its scope, the requirement,
and the corrective action. Examples illustrate detected patterns; they are not an exhaustive
specification.

The shared workflow also runs language-specific formatting, static analysis, tests, coverage checks,
and secret scanning. Those tools can fail independently of the rules below. See
[CONTRIBUTING](https://github.com/savannainstitute/.github/blob/main/CONTRIBUTING.md) for the pull
request process and handling failed checks.

The rule entries describe the proposed release. Existing installations may still follow the
standards main branch with separate local hook revisions. During migration, install a validated
release as a complete bundle. The revised daily monitor reports usage and drift without disabling
workflows, reactivating them, or enabling required checks. Deployment requires release validation
and owner coordination. Existing protections remain in effect.

Coverage reports identify untested lines. Numeric coverage targets are optional and
repository-specific, recorded with a rationale in the selected standards release. Configured targets
block on insufficient coverage or missing measurements. Failed tests block independently of coverage
targets. See [coverage policy configuration](../overrides/README.md#coverage-targets).

Scientific validation is a review responsibility described in CONTRIBUTING. Automated tests and
coverage cannot establish that a method, reference result, or scientific interpretation is correct.

American English applies to project-authored prose. Preserve external identifiers, data values,
quotations, and reference titles. The current spelling check excludes inline backtick literals and
Markdown block quotations. Other false positives remain possible; findings are advisory. Report
incorrect findings rather than changing required literals. A warning does not require a change to an
external interface or scientific meaning.

## Feedback

Report feedback through a standards
[issue](https://github.com/savannainstitute/standards/issues/new) or contact Zack directly. Identify
the rule ID, the affected work, and the practical effect: useful requirements, unclear wording,
unnecessary effort, incorrect findings, or blocked work. Include an example and an alternative where
possible, and state any deadline. Send sensitive examples directly. Submit initial feedback by
November 13, 2026. Continue reporting problems during migration and after the March 5, 2027
compliance deadline.

## Blocking requirements

### decision-attribution

Scope: comments, docstrings, Markdown, configuration files, commit messages and the pull request
text.

Project files describe requirements and decisions without attributing them to a person or date.
Person-and-date annotations, approval credits, and statements of personal requests are rejected.
Retain the technical decision; record its authorship and timing in the pull request or commit
history.

```text
(Name, 2026-10-12)
approved by Name
decided on 2026-10-12
Name asked that
per Name's request
```

### chat-residue

Scope: code files.

Source files must contain complete code. Conversation fragments, Markdown fences, placeholder
comments, and function bodies that only raise NotImplementedError are rejected. Implement the
missing behavior or remove the incomplete code.

```text
here is the updated code
rest of the code unchanged
... existing code
TODO: implement
stop("not implemented")
```

### scratch-file

Scope: file paths.

Scratch files and temporary planning records must not be committed. The check identifies Markdown
and text filenames associated with plans, summaries, time logs, sessions, or notes, and files named
scratch or scratchpad. Keep temporary records outside the repository. Place lasting documentation
under docs/ with a descriptive filename.

```text
notes.md
PLAN.md
time_log.md
scratchpad.py
```

### copy-suffix

Scope: file paths.

Version, new, final, backup, old, copy, and date suffixes in filenames are rejected. Files under
data/ and raw_data/ are exempt. Maintain one current file and use Git history for earlier versions.

```text
analysis_v2.py
model_new.R
report-new.Rmd
run_20221108.R
map_2026-08-24.py
```

### machine-file

Scope: file paths.

Machine-specific files, caches, and build outputs must not be committed. Remove the tracked file and
add its pattern to .gitignore where needed.

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

### notebook-output

Scope: Jupyter notebooks.

Committed Jupyter notebooks must have empty cell outputs. Clear outputs before committing; the
configured pre-commit hook performs this step.

### machine-path

Scope: code files and Markdown.

Paths tied to an individual machine or user account are prohibited. Supply paths through arguments,
configuration, or environment variables.

```text
C:\Users\
/Users/<name>/
/home/<name>/
~/Dropbox/
```

### silenced-check

Scope: code files.

A silenced lint, type or test check names the rule it silences and the reason, on the same line. The
pytest marker needs("reason") is the way to mark a test the hosted check cannot run. Fix the
finding, or write the rule code and the reason after the marker.

```text
# noqa
# type: ignore
# nolint
eslint-disable
shellcheck disable
pragma: no cover
@pytest.mark.skip
@pytest.mark.xfail
# hadolint ignore=DL3008
it.skip("a test name"
```

### always-true-test

Scope: test files.

Tests must include assertions capable of failing when behavior is incorrect. Unconditionally true
assertions are rejected. Use a controlled input and document how the expected result was
independently derived.

```text
assert True
expect_true(TRUE)
expect(true).toBe(true)
```

### untested-code

Scope: code files.

Each source file defining a function or class requires a corresponding test file: `test_<name>.py`,
`test-<name>.R`, or `<name>.test.ts`. Repositories containing code require at least one test file.
Scripts defining no functions or classes do not require an individual test file. Add the indicated
test file and test the behavior defined by the source file.

### readme-path

Scope: README files and docs/.

Repository paths in inline code in README files and docs/ must resolve to existing files or
directories. Correct the path or remove the invalid reference.

### secret-literal

Scope: code files.

A string assigned to a name like password, token, secret or api_key is not committed unless the line
says it is a public fixture and the repo's entry under overrides/ in the standards repo cites where
it is published. Read the value from the environment or a file outside the repo. For a public test
fixture, add the comment and the cited allowlist entry.

### standards-copy

Scope: the files copied from the standards repository.

The caller workflow and local hooks must reference the same full commit SHA. Shared coding-agent
files must match that release. The hosted check verifies the executing workflow revision.
Repository-specific text below the marker in AGENTS.md and CLAUDE.md is excluded from comparison.
This comparison runs on pull requests; local hooks use their pinned version. Use standards-adopt
with the selected release commit to update the workflow, local hooks, and agent files together.

### stray-markdown

Scope: the pull request's changes.

New Markdown files outside docs/ must be listed under a Docs added heading in the pull request
description. README.md files and root AGENTS.md, CLAUDE.md, CHANGELOG.md, NEWS.md, LICENSE.md, and
HOSTING.md are exempt. Place the document under docs/ or list its filename and purpose under that
heading.

### dependency-added

Scope: the pull request's changes.

Dependencies added to pyproject.toml, requirements files, environment.yml, DESCRIPTION, or
package.json must be identified on a Dependencies: line in the pull request description. List each
added package and its purpose.

### test-removed

Scope: the pull request's changes.

Removed test functions must be identified under a Tests removed or skipped heading in the pull
request description. List each removed test and the reason, or retain the test.

### fix-without-test

Scope: the pull request's changes.

Changes to source under src/, R/, or packages/ must include at least one added line under tests/ or
a No test because line in the pull request description. Add a regression test that fails without the
change, or explain why a test change is unnecessary.

### attribution

Scope: commit messages and the pull request text.

Commit messages and pull request descriptions must omit coding-tool attribution, including
model-vendor co-author trailers, generated-with statements, and vendor noreply addresses. Remove the
attribution and use the repository settings that disable automatic tool credits.

```text
Co-authored-by: Claude <noreply@anthropic.com>
Generated with [Claude Code]
```

### installer-committed

Scope: file paths.

Third-party software distributions, including wheels, executables, and installers, must not be
committed. Remove the distribution and document installation in the README or environment
specification.

```text
metashape.whl
setup.exe
tool.msi
app.dmg
lib.deb
```

### binary-outside-lfs

Scope: the pull request's changes.

A pull request that adds a binary file (an image, raster, point cloud, video, model, archive, PDF,
spreadsheet or R data file; SVG is text) adds it through Git LFS: the path matches a filter=lfs line
in .gitattributes and the committed file is the LFS pointer. Run git lfs install once, add the
pattern to .gitattributes with git lfs track, and commit the file again. A large or growing
collection belongs in object storage, named in data/README.md.

## Advisory findings

### contrast

Scope: comments, docstrings and Markdown, commit messages and the pull request text.

State requirements directly. Rhetorical contrast constructions are flagged for review. Remove the
unnecessary comparison.

```text
not X, but Y
isn't X, it's Y
it's X, never Y
this is X, not Y
```

### narration

Scope: comments, commit messages and the pull request text.

Comments describe constraints and behavior. Conversational instructions and accounts of the editing
process are flagged. Replace editing commentary with the relevant technical information, or remove
it.

```text
now we handle
updated to fix
as requested
changed this to
per your feedback
```

### banner

Scope: code files.

Comment blocks of three or more consecutive lines and decorative divider lines are flagged.
Configuration files, roxygen comments, and block comments in languages using slash-style comments
are exempt. Use concise comments; place longer explanations in docstrings or documentation.

### docstring-history

Scope: comments and docstrings.

Dates and change-history language in comments and docstrings are flagged. Describe current purpose
and behavior. Preserve change history in commits and pull requests.

```text
2023-04-01
originally
historically
because the previous
```

### typography

Scope: every tracked file.

No em dashes or emoji anywhere; no bold in Markdown; none of the words below written in capitals for
emphasis in a comment or Markdown. A capitalized identifier or acronym is fine. Use a comma, a
period or a plain word.

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

### sales-vocabulary

Scope: comments, docstrings and Markdown, commit messages and the pull request text.

No sales vocabulary. Say what the code does.

```text
robust
comprehensive
seamless
production-ready
```

### british-spelling

Scope: comments, docstrings and Markdown, commit messages and the pull request text.

Project prose uses American English. The check excludes code identifiers and library argument names.
Inline backtick literals and Markdown block quotations are excluded from spelling checks. Replace
flagged spellings with their American English equivalents.

```text
colour
behaviour
analyse
centre
labelled
grey
```

### silent-default

Scope: code files.

Fallback values for required inputs are flagged for review. Raise an error when required input is
absent, or document why the default is valid.

```text
.get(key, None)
.get(key, "")
x %||% y
ifelse(is.na(x), 0, x)
x ?? null
```

### unsourced-constant

Scope: code files.

A numeric constant assigned to an uppercase name requires a source comment on the same or preceding
line. Identify the configuration, dataset, publication, or measurement that supplies the value.

### swallowed-error

Scope: R files.

R error handlers that discard failures are flagged. Python equivalents are checked by Ruff rules
E722, BLE001, S110, and S112. Propagate the error or explicitly handle and document the expected
failure condition.

```text
tryCatch(..., error = function(e) NULL)
try(..., silent = TRUE)
```

### unverified-citation

Scope: every tracked file.

A DOI requires an accompanying source URL. Provide the URL used to verify the reference. A URL makes
the reference traceable; the automated check cannot establish that it was read.

### synthetic-fallback

Scope: code files.

Substitution of example or synthetic data when an input file is missing is flagged for review. Fail
explicitly for missing required inputs. Identify intentional example datasets in data/README.md.

```text
sample
example
synthetic
dummy
rnorm
runif
np.random
```

### silent-row-drop

Scope: code files.

Calls that drop or fill missing rows require a same-line comment stating the count or reason.
Document the treatment of missing values and report affected row counts in the output.

```text
dropna(
fillna(
na.omit(
drop_na(
filter(!is.na(
```

### data-unlisted

Scope: files under data/.

Each file under data/ must be listed in data/README.md with its source, date, license, units, and
input or output status. Add the missing entry or move a file that does not belong in data/.

## Maintaining this reference

The rule descriptions are generated from `src/standards/rules.py` using `render-rules`. Update that
source and regenerate this file when revising a rule description.

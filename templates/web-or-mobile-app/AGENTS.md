# Rules for coding agents

Every pull request in this repository runs the organization's check, which appears as
`checks / lint` and blocks the merge when it fails. The rules below are that check's list, with the
same ids its findings print. The full list with every shape the check looks for is at
<https://github.com/savannainstitute/standards/blob/main/docs/RULES.md>.

## Before you commit

- Run `pre-commit run --all-files`. It runs the same check on this computer. Fix each finding it
  prints; do not silence it.
- This repository holds no linter settings. They live in the organization's standards repository,
  and a settings file added here is ignored.
- Write commit messages and pull request text that say what the change does. Add no tool
  attribution: no co-author trailer and no generated-with line.
- The pull request text is read by the check. A new dependency is named on a `Dependencies:` line. A
  new Markdown file outside the docs folder is listed under a `Docs added` heading. A removed test
  is listed under a `Tests removed or skipped` heading. A source change with no test carries a
  `No test because` line.
- A test the hosted check cannot run is marked with what it needs, such as
  `@pytest.mark.needs("a GPU")`. A bare skip is refused.
- A test asserts on a value computed from a planted input, and the comment beside the expected value
  derives it.

## Rules that block the merge

- `decision-attribution`: Project files describe requirements and decisions without attributing them
  to a person or date. Person-and-date annotations, approval credits, and statements of personal
  requests are rejected. To fix it: Retain the technical decision; record its authorship and timing
  in the pull request or commit history.

  ```text
  (Name, 2026-10-12)
  approved by Name
  decided on 2026-10-12
  Name asked that
  per Name's request
  ```

- `chat-residue`: Source files must contain complete code. Conversation fragments, Markdown fences,
  placeholder comments, and function bodies that only raise NotImplementedError are rejected. To fix
  it: Implement the missing behavior or remove the incomplete code.

  ```text
  here is the updated code
  rest of the code unchanged
  ... existing code
  TODO: implement
  stop("not implemented")
  ```

- `scratch-file`: Scratch files and temporary planning records must not be committed. The check
  identifies Markdown and text filenames associated with plans, summaries, time logs, sessions, or
  notes, and files named scratch or scratchpad. To fix it: Keep temporary records outside the
  repository. Place lasting documentation under docs/ with a descriptive filename.

  ```text
  notes.md
  PLAN.md
  time_log.md
  scratchpad.py
  ```

- `copy-suffix`: Version, new, final, backup, old, copy, and date suffixes in filenames are
  rejected. Files under data/ and raw_data/ are exempt. To fix it: Maintain one current file and use
  Git history for earlier versions.

  ```text
  analysis_v2.py
  model_new.R
  report-new.Rmd
  run_20221108.R
  map_2026-08-24.py
  ```

- `machine-file`: Machine-specific files, caches, and build outputs must not be committed. To fix
  it: Remove the tracked file and add its pattern to .gitignore where needed.

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

- `notebook-output`: Committed Jupyter notebooks must have empty cell outputs. To fix it: Clear
  outputs before committing; the configured pre-commit hook performs this step.

- `machine-path`: Paths tied to an individual machine or user account are prohibited. To fix it:
  Supply paths through arguments, configuration, or environment variables.

  ```text
  C:\Users\
  /Users/<name>/
  /home/<name>/
  ~/Dropbox/
  ```

- `silenced-check`: A silenced lint, type or test check names the rule it silences and the reason,
  on the same line. The pytest marker needs("reason") is the way to mark a test the hosted check
  cannot run. To fix it: Fix the finding, or write the rule code and the reason after the marker.

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

- `always-true-test`: Tests must include assertions capable of failing when behavior is incorrect.
  Unconditionally true assertions are rejected. To fix it: Use a controlled input and document how
  the expected result was independently derived.

  ```text
  assert True
  expect_true(TRUE)
  expect(true).toBe(true)
  ```

- `untested-code`: Each source file defining a function or class requires a corresponding test file:
  `test_<name>.py`, `test-<name>.R`, or `<name>.test.ts`. Repositories containing code require at
  least one test file. Scripts defining no functions or classes do not require an individual test
  file. To fix it: Add the indicated test file and test the behavior defined by the source file.

- `readme-path`: Repository paths in inline code in README files and docs/ must resolve to existing
  files or directories. To fix it: Correct the path or remove the invalid reference.

- `secret-literal`: A string assigned to a name like password, token, secret or api_key is not
  committed unless the line says it is a public fixture and the repo's entry under overrides/ in the
  standards repo cites where it is published. To fix it: Read the value from the environment or a
  file outside the repo. For a public test fixture, add the comment and the cited allowlist entry.

- `standards-copy`: The caller workflow and shared coding-agent files must match the central copies.
  The pre-commit configuration must reference the standards hooks at a commit. Repository-specific
  text below the marker in AGENTS.md and CLAUDE.md is excluded from comparison. This comparison runs
  on pull requests; local hooks use their pinned version. To fix it: Restore the indicated file from
  the appropriate project template. Use pre-commit autoupdate to update local hook versions.

- `stray-markdown`: New Markdown files outside docs/ must be listed under a Docs added heading in
  the pull request description. README.md files and root AGENTS.md, CLAUDE.md, CHANGELOG.md,
  NEWS.md, LICENSE.md, and HOSTING.md are exempt. To fix it: Place the document under docs/ or list
  its filename and purpose under that heading.

- `dependency-added`: Dependencies added to pyproject.toml, requirements files, environment.yml,
  DESCRIPTION, or package.json must be identified on a Dependencies: line in the pull request
  description. To fix it: List each added package and its purpose.

- `test-removed`: Removed test functions must be identified under a Tests removed or skipped heading
  in the pull request description. To fix it: List each removed test and the reason, or retain the
  test.

- `fix-without-test`: Changes to source under src/, R/, or packages/ must include at least one added
  line under tests/ or a No test because line in the pull request description. To fix it: Add a
  regression test that fails without the change, or explain why a test change is unnecessary.

- `attribution`: Commit messages and pull request descriptions must omit coding-tool attribution,
  including model-vendor co-author trailers, generated-with statements, and vendor noreply
  addresses. To fix it: Remove the attribution and use the repository settings that disable
  automatic tool credits.

  ```text
  Co-authored-by: Claude <noreply@anthropic.com>
  Generated with [Claude Code]
  ```

- `installer-committed`: Third-party software distributions, including wheels, executables, and
  installers, must not be committed. To fix it: Remove the distribution and document installation in
  the README or environment specification.

  ```text
  metashape.whl
  setup.exe
  tool.msi
  app.dmg
  lib.deb
  ```

- `binary-outside-lfs`: A pull request that adds a binary file (an image, raster, point cloud,
  video, model, archive, PDF, spreadsheet or R data file; SVG is text) adds it through Git LFS: the
  path matches a filter=lfs line in .gitattributes and the committed file is the LFS pointer. To fix
  it: Run git lfs install once, add the pattern to .gitattributes with git lfs track, and commit the
  file again. A large or growing collection belongs in object storage, named in data/README.md.

## Rules that warn

- `contrast`: State requirements directly. Rhetorical contrast constructions are flagged for review.
  To fix it: Remove the unnecessary comparison.

  ```text
  not X, but Y
  isn't X, it's Y
  it's X, never Y
  this is X, not Y
  ```

- `narration`: Comments describe constraints and behavior. Conversational instructions and accounts
  of the editing process are flagged. To fix it: Replace editing commentary with the relevant
  technical information, or remove it.

  ```text
  now we handle
  updated to fix
  as requested
  changed this to
  per your feedback
  ```

- `banner`: Comment blocks of three or more consecutive lines and decorative divider lines are
  flagged. Configuration files, roxygen comments, and block comments in languages using slash-style
  comments are exempt. To fix it: Use concise comments; place longer explanations in docstrings or
  documentation.

- `docstring-history`: Dates and change-history language in comments and docstrings are flagged. To
  fix it: Describe current purpose and behavior. Preserve change history in commits and pull
  requests.

  ```text
  2023-04-01
  originally
  historically
  because the previous
  ```

- `typography`: No em dashes or emoji anywhere; no bold in Markdown; none of the words below written
  in capitals for emphasis in a comment or Markdown. A capitalized identifier or acronym is fine. To
  fix it: Use a comma, a period or a plain word.

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

- `sales-vocabulary`: No sales vocabulary. To fix it: Say what the code does.

  ```text
  robust
  comprehensive
  seamless
  production-ready
  ```

- `british-spelling`: Project prose uses American English. The check excludes code identifiers and
  library argument names. To fix it: Replace flagged spellings with their American English
  equivalents.

  ```text
  colour
  behaviour
  analyse
  centre
  labelled
  grey
  ```

- `silent-default`: Fallback values for required inputs are flagged for review. To fix it: Raise an
  error when required input is absent, or document why the default is valid.

  ```text
  .get(key, None)
  .get(key, "")
  x %||% y
  ifelse(is.na(x), 0, x)
  x ?? null
  ```

- `unsourced-constant`: A numeric constant assigned to an uppercase name requires a source comment
  on the same or preceding line. To fix it: Identify the configuration, dataset, publication, or
  measurement that supplies the value.

- `swallowed-error`: R error handlers that discard failures are flagged. Python equivalents are
  checked by Ruff rules E722, BLE001, S110, and S112. To fix it: Propagate the error or explicitly
  handle and document the expected failure condition.

  ```text
  tryCatch(..., error = function(e) NULL)
  try(..., silent = TRUE)
  ```

- `unverified-citation`: A DOI requires an accompanying source URL. To fix it: Provide the URL used
  to verify the reference. A URL makes the reference traceable; the automated check cannot establish
  that it was read.

- `synthetic-fallback`: Substitution of example or synthetic data when an input file is missing is
  flagged for review. To fix it: Fail explicitly for missing required inputs. Identify intentional
  example datasets in data/README.md.

  ```text
  sample
  example
  synthetic
  dummy
  rnorm
  runif
  np.random
  ```

- `silent-row-drop`: Calls that drop or fill missing rows require a same-line comment stating the
  count or reason. To fix it: Document the treatment of missing values and report affected row
  counts in the output.

  ```text
  dropna(
  fillna(
  na.omit(
  drop_na(
  filter(!is.na(
  ```

- `data-unlisted`: Each file under data/ must be listed in data/README.md with its source, date,
  license, units, and input or output status. To fix it: Add the missing entry or move a file that
  does not belong in data/.

<!-- Organization copy above; this repository's notes go below. -->

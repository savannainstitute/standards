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

- `decision-attribution`: A file states what holds, not who decided it or when: no person and date
  in parentheses, no decision credited to a person or a date, no line saying what a person asked for
  or wants. To fix it: State the decision itself. The pull request and git history record who made
  it and when.

  ```text
  (Name, 2026-10-12)
  approved by Name
  decided on 2026-10-12
  Name asked that
  per Name's request
  ```

- `chat-residue`: No chat left in source: Markdown fences, phrases from a conversation, placeholder
  comments standing in for code, or a function body that only raises NotImplementedError. To fix it:
  Finish the code or remove the stub.

  ```text
  here is the updated code
  rest of the code unchanged
  ... existing code
  TODO: implement
  stop("not implemented")
  ```

- `scratch-file`: No scratch or planning files committed: a Markdown or text file named for a plan,
  summary, time log, session or notes, or any file named scratch or scratchpad. To fix it: Keep them
  out of the repo, or move a lasting document under docs/ with a name that says what it holds.

  ```text
  notes.md
  PLAN.md
  time_log.md
  scratchpad.py
  ```

- `copy-suffix`: No versions kept as copies: a version, new, final, backup, old or copy suffix, or a
  date in a file name. Files under data/ and raw_data/ are exempt. To fix it: Keep one file; git
  history holds the versions.

  ```text
  analysis_v2.py
  model_new.R
  report-new.Rmd
  run_20221108.R
  map_2026-08-24.py
  ```

- `machine-file`: No machine files, caches or build output. To fix it: Delete the file and add the
  pattern to .gitignore if it is missing.

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

- `notebook-output`: A committed notebook carries no cell outputs. To fix it: Clear outputs before
  committing; the pre-commit hook does it.

- `machine-path`: No machine-specific paths. To fix it: Take the path from an argument, a config
  file or an environment variable.

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

- `always-true-test`: No test that cannot fail. To fix it: Assert on a value computed from a planted
  input whose expected answer is derived in a comment.

  ```text
  assert True
  expect_true(TRUE)
  expect(true).toBe(true)
  ```

- `untested-code`: A code file that defines a function or a class has its own test file, named as
  the layouts name it: `test_<name>.py`, `test-<name>.R` or `<name>.test.ts`. A repository with code
  and no test file at all fails once. Files that define nothing, such as scripts that only run
  steps, need no test file of their own. To fix it: Add the test file the finding names, testing
  what the code file defines.

- `readme-path`: Every path named in backticks in a README or a docs/ file exists in the repo. To
  fix it: Fix the path or remove the sentence.

- `secret-literal`: A string assigned to a name like password, token, secret or api_key is not
  committed unless the line says it is a public fixture and the repo's entry under overrides/ in the
  standards repo cites where it is published. To fix it: Read the value from the environment or a
  file outside the repo. For a public test fixture, add the comment and the cited allowlist entry.

- `standards-copy`: The caller workflow and the files for coding agents match the standards
  repository's copies, and .pre-commit-config.yaml runs the standards hooks at any commit. Text
  below the marker line in AGENTS.md and CLAUDE.md belongs to the repository and is not compared.
  Checked on the pull request only, since pre-commit runs the commit the repository pins. To fix it:
  Copy the file the finding names from the template for this kind of project in the standards
  repository. To run newer hooks on your computer, run pre-commit autoupdate.

- `stray-markdown`: A pull request that adds a Markdown file outside docs/, other than a README.md
  or the root AGENTS.md, CLAUDE.md, CHANGELOG.md, NEWS.md, LICENSE.md or HOSTING.md, lists it in the
  pull request text under a Docs added heading. To fix it: Move the file under docs/, or list it
  under a Docs added heading with one line on why it exists.

- `dependency-added`: A pull request that adds a dependency to pyproject.toml, a requirements file,
  environment.yml, DESCRIPTION or package.json names it in the pull request text on a Dependencies:
  line. To fix it: Add a Dependencies: line naming each new package and what it is for.

- `test-removed`: A pull request that removes a test function lists it in the pull request text
  under a Tests removed or skipped heading. To fix it: Keep the test, or list it under that heading
  with the reason.

- `fix-without-test`: A pull request that changes source under src/, R/ or packages/ adds at least
  one line under tests/, or carries a No test because line in the pull request text. To fix it: Add
  the test that fails without the change, or write the No test because line.

- `attribution`: No tool attribution in a commit message or pull request text: no co-author trailer
  naming a model vendor, no generated-with line, no vendor noreply address. To fix it: Remove the
  trailer or line; the committed project settings turn it off.

  ```text
  Co-authored-by: Claude <noreply@anthropic.com>
  Generated with [Claude Code]
  ```

- `installer-committed`: Someone else's software is never committed: no wheel, executable or
  installer. To fix it: Delete the file; the README or the environment file says where to get the
  program.

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

- `contrast`: No contrast constructions used for effect. To fix it: State the point directly; drop
  the half of the sentence that names what it is not.

  ```text
  not X, but Y
  isn't X, it's Y
  it's X, never Y
  this is X, not Y
  ```

- `narration`: A comment states a constraint or an invariant; it does not narrate the change or the
  conversation. To fix it: Delete the comment, or rewrite it to say what the code must hold true.

  ```text
  now we handle
  updated to fix
  as requested
  changed this to
  per your feedback
  ```

- `banner`: No comment block of three or more consecutive comment lines, and no divider line of
  dashes, equals signs or asterisks. Configuration files, roxygen comments and block comments in the
  slash languages are exempt. To fix it: Keep one line that states the constraint; move anything
  longer to the docstring or docs/.

- `docstring-history`: A docstring or comment states purpose, not history: no dates and no account
  of what the code did before. To fix it: Git history is the record; remove the history from the
  docstring.

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

- `british-spelling`: Prose is written in American English. Code is not read, since a library's own
  argument and function names are what they are. To fix it: Use the American spelling.

  ```text
  colour
  behaviour
  analyse
  centre
  labelled
  grey
  ```

- `silent-default`: A required input has no silent default; the shapes below are reported for
  review. To fix it: Raise or stop when the input is missing, or state why the default is correct.

  ```text
  .get(key, None)
  .get(key, "")
  x %||% y
  ifelse(is.na(x), 0, x)
  x ?? null
  ```

- `unsourced-constant`: A numeric constant assigned to an upper-case name carries its source in a
  comment on the same or the previous line. To fix it: Write where the number comes from: a config
  file, the data, a paper, a measurement.

- `swallowed-error`: An error is not swallowed. Python's equivalents are ruff rules E722, BLE001,
  S110 and S112. To fix it: Let the error propagate, or handle the one case you expect and say
  which.

  ```text
  tryCatch(..., error = function(e) NULL)
  try(..., silent = TRUE)
  ```

- `unverified-citation`: A DOI carries a URL beside it, so the reference was read and can be
  followed. To fix it: Add the URL you read it from, or remove the citation.

- `synthetic-fallback`: No example or synthetic data as a fallback when a file is missing: a
  missing-file test beside the words below is reported for review. To fix it: Fail when the input is
  missing. Example data is declared in data/README.md, never substituted.

  ```text
  sample
  example
  synthetic
  dummy
  rnorm
  runif
  np.random
  ```

- `silent-row-drop`: A call that drops or fills missing rows carries a comment on the same line
  stating the count or the reason. To fix it: Report how many rows are dropped and why, in the
  comment and in the output.

  ```text
  dropna(
  fillna(
  na.omit(
  drop_na(
  filter(!is.na(
  ```

- `data-unlisted`: Every file under data/ is named in data/README.md, which gives its source, date,
  license and units and says whether it is an input or an output. To fix it: Add a line for the file
  to data/README.md, or move the file.

<!-- Organization copy above; this repository's notes go below. -->

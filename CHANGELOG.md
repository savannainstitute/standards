# Changelog

## Unreleased

Changes collect here and are released together when a repository needs them.

- `decision-attribution` blocks the merge. It no longer reads "said", and reads "per" only
  before a possessive or a date, after a measurement on every repository in the organization.
- `standards-copy` accepts a pre-commit pin to any release with the current major version, so
  a new release no longer asks every repository to move its pin.
- Every Dockerfile in a repository is linted with hadolint 2.15.1, and any finding fails.
- The agent hook runs when Claude Code, Codex or Gemini ends its turn, and sends the agent
  back once to fix the writing-rule lines in the files it changed. A new shared file,
  `.codex/hooks.json`, and new entries in `.claude/settings.json` and `.gemini/settings.json`.

## 1.2.0

- A new rule, `untested-code`, blocks: a code file that defines a function or a class needs its
  own test file, and a repository with code and no tests fails.
- Test coverage is reported for Python and JavaScript, and a repository needs 75% of its lines
  covered. One that joined below that may not fall below its recorded start, and each pull
  request must cover 90% of the code lines it changes until the repository reaches 75%.
- A new rule, `decision-attribution`, warns on a decision credited to a person or a date.
- The `typography` rule no longer looks for curly quotes.
- Ruff allows a single capital letter, such as `X`, as a variable name.
- `standards-copy` reports a shared file that git does not track.
- Every repository moves its pre-commit `rev` to `v1.2.0`.

## 1.1.0

- The files for coding agents (`AGENTS.md`, `CLAUDE.md`, the Claude Code settings and hook, the
  Gemini settings), rendered from the rule list with `render-agent`.
- A new rule, `standards-copy`: a repository's caller workflow, agent files and pre-commit pin
  must match the copies here. Every repository moves its pre-commit `rev` to `v1.1.0`.
- R checks: Air, lintr, testthat, and help pages that match the code for a package.
- JavaScript and TypeScript checks: ESLint, Prettier, the TypeScript compiler and vitest.
- The five writing-style rules (`contrast`, `narration`, `banner`, `typography`,
  `sales-vocabulary`) now warn and no longer block a merge.
- Markdown is linted with markdownlint in every repository.
- A pipeline's tests run inside its conda environment in a second job, `conda-tests`.
- Five more templates: R package, R analysis, Shiny app, web or mobile app, and documentation
  and configuration.

## 1.0.0

First release: the rule list and its check, the reusable check workflow, the Python linter
settings, the pre-commit hooks, and the Python pipeline template.

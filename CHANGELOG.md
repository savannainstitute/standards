# Changelog

## 1.1.0

- The files for coding agents (`AGENTS.md`, `CLAUDE.md`, the Claude Code settings and hook, the
  Gemini settings), rendered from the rule list with `render-agent`.
- A new rule, `standards-copy`: a repository's caller workflow, agent files and pre-commit pin
  must match the copies here. Every repository moves its pre-commit `rev` to `v1.1.0`.
- R checks: Air, lintr, testthat, and help pages that match the code for a package.
- JavaScript and TypeScript checks: ESLint, Prettier, the TypeScript compiler and vitest.
- Markdown is linted with markdownlint in every repository.
- A pipeline's tests run inside its conda environment in a second job, `conda-tests`.
- Five more templates: R package, R analysis, Shiny app, web or mobile app, and documentation
  and configuration.

## 1.0.0

First release: the rule list and its check, the reusable check workflow, the Python linter
settings, the pre-commit hooks, and the Python pipeline template.

# Savanna Institute code standards

This repository holds the checks that every Savanna Institute repository runs on each pull request,
the settings those checks use, and the templates new repositories start from. Nothing here needs to
be installed by hand: a repository runs the checks through one short workflow file, and the same
checks can run on your own computer before you commit.

## What the check does

When you open a pull request, a check named `checks / lint` runs. It looks at seven things, and
skips the ones for a language the repository does not use:

1. Secrets. Any password, token or key committed anywhere in the repository's history fails the
   check.
2. Python style. Code is formatted and linted with ruff, using the settings in
   `src/standards/configs/ruff.toml`. The settings cannot be changed inside your repository.
3. R style. Code is formatted with Air and linted with lintr, using `src/standards/configs/air.toml`
   and `src/standards/r/lintr_settings.R`. A package's help pages must match its code.
4. JavaScript and TypeScript style and types, with ESLint, Prettier and the TypeScript compiler,
   using the settings in `src/standards/configs/`.
5. YAML files are well formed. Markdown is formatted like code: Prettier wraps it to 100 columns and
   lines up its tables, and markdownlint checks the rest. Every Dockerfile passes hadolint with the
   settings in `src/standards/configs/hadolint.yaml`.
6. Tests. Python tests run with pytest, R tests with testthat and JavaScript tests with vitest.
   Every file of code that defines a function needs its own test file. The tests must run at least
   75% of the lines of Python and JavaScript code. A repository that was below that when it joined
   the standard may not fall below where it started, and each pull request must test at least 90% of
   the code lines it changes until the repository reaches 75%. The numbers are in
   `src/standards/configs/coverage.yaml`.
7. The rules in `docs/RULES.md`. Each rule says what it looks for, whether it blocks the merge or
   only warns, and how to fix a finding.

The rules about writing style (dashes and capitals, long comment blocks, a few phrasings and words)
only warn. What blocks is what nobody would defend: a secret, a machine file, chat left in source, a
silenced check with no reason, a removed test with no explanation.

A failing check prints one line per finding: the file, the line, the rule, and what to change. Every
part of the check runs even when an earlier part fails, so one push shows every finding. Fix them
and push again; the check runs again on its own.

## Running the checks on your own computer

Each repository made from a template carries a `.pre-commit-config.yaml` that runs the same checks
when you commit. Install Python 3.11 or later and Node.js 24 including npm. The Markdown hook
downloads the pinned Prettier version into npm's cache on first use; subsequent runs reuse it.
Install pre-commit once:

```text
pip install pre-commit
pre-commit install
```

After that, every commit runs the checks on the files you changed. To run them over the whole
repository:

```text
pre-commit run --all-files
```

The pull request rules (a new dependency with no explanation, a removed test, a changed source file
with no test) need the pull request itself and run only on GitHub. Every new pull request in the
organization starts from the template in the organization's `.github` repository, which carries the
headings those rules read; write under a heading when it applies and leave it alone when it does
not.

## Tests the hosted check cannot run

A test that needs a GPU, a licensed program, another operating system or an outside service carries
a marker that says what it needs:

```python
@pytest.mark.needs("a Metashape license")
def test_reconstruction(): ...
```

The hosted check leaves those tests out and prints how many it left out and why. On your own
machine, `pytest` with no options runs them all. R and JavaScript tests have the same marker: the R
templates carry it as `needs("a reason")` in a helper file under their tests folder, and the web
template carries it in its tests folder as well. Each template's README shows how to use it.

## Files for coding agents

Use the [scientific review record](docs/scientific-review.md) for changes to scientific behavior.
The [adoption and recovery procedure](docs/adoption-review.md) provides the pilot, writing-review,
compute, and backup-administration records.

Every repository carries the same seven files for people who work with a coding agent such as Claude
Code, Codex or Gemini:

- `AGENTS.md`: the rules, written as instructions. Codex reads it on its own.
- `CLAUDE.md`: one line that makes Claude Code read `AGENTS.md`.
- `.gemini/settings.json`: makes Gemini read `AGENTS.md`, and runs the hook when Gemini ends its
  turn.
- `.codex/hooks.json`: runs the hook when Codex ends its turn.
- `.claude/settings.json`: turns off the attribution lines Claude Code adds to commits and pull
  requests, and runs the hook below.
- `.claude/hooks/rules_hook.py` and `.claude/hooks/rules_hook.json`: the hook. When the agent ends
  its turn, the hook runs pre-commit on every file changed in the working tree, if pre-commit is
  installed, and reads those files for the writing rules and for a decision credited to a person or
  a date. If pre-commit fails or a line would be reported, it sends the agent back once with the
  list to fix. It also tells Claude Code, after each file it writes, which lines the check will
  report, and stops it from deleting a folder outside the project. It never refuses a write. The
  hook needs Python on your computer, as `python`.

Without pre-commit, the hook covers only the writing rules and `decision-attribution`, which it can
read with Python alone. With pre-commit installed, the agent also gets Ruff's fixes and findings and
the rule check before it finishes. Air, lintr, markdownlint and the tests run only in the check on
the pull request.

The hook scripts require Python; the full local check also requires pre-commit and Node.js as
described above. Verify that the installed agent loads the project configuration and runs a planted
test finding. Codex requires project trust and review of new or changed hooks through `/hooks`, as
described in the [official hook documentation](https://learn.chatgpt.com/docs/hooks). A tested hook
script does not establish that every client version loads it. Gemini CLI configuration does not
establish Antigravity support. Run pre-commit explicitly if hooks are unavailable. Local hooks are
optional; required pull-request checks provide enforcement.

A repository may add its own notes to `AGENTS.md` and `CLAUDE.md` below the marker line; everything
above it, and the other five files, must match the copies here, and the check says so when they do
not.

## Layout of this repository

- `src/standards/`: the `standards` Python package. `src/standards/rules.py` is the rule list,
  `src/standards/rules_check.py` is the check, `src/standards/configs/` holds the linter settings.
- `src/standards/agent/`: the organization's copy of the files for coding agents. `AGENTS.md` and
  the hook's patterns are rendered from the rule list with `render-agent`, which also refreshes the
  copies at the root of this repository and in each template.
- `docs/RULES.md`: the rule list, rendered from `src/standards/rules.py`.
- `.github/workflows/checks.yml`: the reusable workflow every repository calls.
- `.pre-commit-hooks.yaml`: the hooks a repository's `.pre-commit-config.yaml` points at.
- `templates/`: one folder per kind of project; a new repository is generated from one.
- `overrides/`: per-repository exceptions, each in a folder named for the repository.
- `tests/`: the self-test. Every rule is planted in a fixture and caught.

## Changing a rule

Open a pull request here. The rule list is `src/standards/rules.py`; `docs/RULES.md` is rendered
from it with `render-rules` and the files for coding agents with `render-agent`, and the self-test
fails if either is out of date or if a rule has no planted example. Repositories adopt a tested
commit through an update pull request. The workflow and local hooks must reference that same commit;
agent files must match the selected release. Do not update hooks independently with
`pre-commit autoupdate`.

## Adopting and rolling back a release

The standards maintainer validates a release on representative Python, R, and application projects
before recommending its full commit SHA. With that commit available in a local standards checkout,
prepare the consumer's update on a branch:

```sh
standards-adopt --repo-dir PROJECT --standards-root STANDARDS --revision FULL_COMMIT_SHA
```

The command reads committed files at the selected revision, updates the caller, hooks, and agent
files together, and preserves project instructions below the agent-file marker. Other pre-commit
repositories and configured hooks are retained. Inspect the diff, run local checks, and open a pull
request. The command does not commit, push, merge, or change repository protections. It rejects a
moving reference or missing release files before writing the bundle.

To roll back, run the same command with the previous release's full SHA and test the resulting pull
request. A failed update is left unmerged. The creation workflow performs this installation after
copying the project template, so its workflow and hook pins identify the selected release rather
than a template's seed revision. Existing installations following main require a coordinated
migration; publishing a release does not repin those repositories automatically.

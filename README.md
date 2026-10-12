# Savanna Institute code standards

This repository holds the checks that every Savanna Institute repository runs on each pull
request, the settings those checks use, and the templates new repositories start from. Nothing
here needs to be installed by hand: a repository runs the checks through one short workflow
file, and the same checks can run on your own computer before you commit.

## What the check does

When you open a pull request, a check named `checks / lint` runs. It looks for four things:

1. Secrets. Any password, token or key committed anywhere in the repository's history fails
   the check.
2. Python style. Code is formatted and linted with ruff, using the settings in
   `src/standards/configs/ruff.toml`. The settings cannot be changed inside your repository.
3. YAML files are well formed.
4. The rules in `docs/RULES.md`. Each rule says what it looks for, whether it blocks the merge
   or only warns, and how to fix a finding.

A failing check prints one line per finding: the file, the line, the rule, and what to change.
Fix the finding and push again; the check runs again on its own.

## Running the checks on your own computer

Each repository made from a template carries a `.pre-commit-config.yaml` that runs the same
checks when you commit. Install pre-commit once:

```text
pip install pre-commit
pre-commit install
```

After that, every commit runs the checks on the files you changed. To run them over the whole
repository:

```text
pre-commit run --all-files
```

The pull request rules (a new dependency with no explanation, a removed test, a changed source
file with no test) need the pull request itself and run only on GitHub.

## Tests the hosted check cannot run

A test that needs a GPU, a licensed program, another operating system or an outside service
carries a marker that says what it needs:

```python
@pytest.mark.needs("a Metashape license")
def test_reconstruction(): ...
```

The hosted check leaves those tests out and prints how many it left out and why. On your own
machine, `pytest` with no options runs them all.

## Layout of this repository

- `src/standards/`: the `standards` Python package. `src/standards/rules.py` is the rule list,
  `src/standards/slop_check.py` is the check, `src/standards/configs/` holds the linter settings.
- `docs/RULES.md`: the rule list, rendered from `src/standards/rules.py`.
- `.github/workflows/checks.yml`: the reusable workflow every repository calls.
- `.pre-commit-hooks.yaml`: the hooks a repository's `.pre-commit-config.yaml` points at.
- `templates/`: one folder per kind of project; a new repository is generated from one.
- `overrides/`: per-repository exceptions, each in a folder named for the repository.
- `tests/`: the self-test. Every rule is planted in a fixture and caught.

## Changing a rule

Open a pull request here. The rule list is `src/standards/rules.py`; `docs/RULES.md` is
rendered from it with `render-rules`, and the self-test fails if the two disagree or if a rule
has no planted example. Repositories pick up a merged change on their next pull request; the
pre-commit hooks pick it up when the repository's `.pre-commit-config.yaml` is moved to the
new version tag.

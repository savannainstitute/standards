# Per-repository exceptions

The checks read no settings from the repository they check. When one repository needs an exception,
it is recorded here, in a folder named after that repository, and reaches the check through a pull
request to this repository.

Repository policies and exceptions are reviewed through pull requests.

## A file exempt from a rule

`overrides/<repository>/exempt.yaml` lists paths and the rules they are exempt from, each with a
reason:

```yaml
exempt:
  - path: src/standards/rules.py
    rules: [chat-residue]
    reason: the rule examples in this file are the shapes the rule looks for
```

An entry with no reason, or naming a rule that does not exist, stops the check with an error.

## A public test fixture

A test account password that a public project publishes in its own documentation, such as a database
image's default login, may appear in source if the line says so and the fixture is listed in
`overrides/<repository>/public_fixtures.yaml` with the page it comes from:

```yaml
public_fixtures:
  - value: the-literal-as-it-appears-in-source
    published_at: https://the.page/that/publishes/it
```

A line in that repository then passes the secret-literal rule when it carries the words "public
fixture" in a comment and its literal matches an entry whose `published_at` is a URL.

## Coverage targets

Coverage is reported by default. Failed tests still fail CI. A repository owner and reviewer select
any numeric targets based on the project's intended use, consequences of failure, and existing
tests. Record the behavior and failure cases that need testing in the project documentation,
including scientific reference cases where applicable. A percentage does not replace that evidence.

To enforce targets, add `overrides/<repository>/coverage.yaml` in this standards repository:

```yaml
floor_percent: 60
changed_lines_percent: 80
rationale: Preserve the tested import and export paths while extending validation of new inputs.
```

The numbers illustrate configuration; they are not recommended defaults. Each target is optional and
must be between 0 and 100. A rationale is required. The overall target applies to every measured
run; the changed-line target applies whenever a pull request base is supplied, even if overall
coverage exceeds its target. A change with no measured executable lines has no changed-line target
to evaluate. Push runs without a base report that the changed-line comparison was not performed.
Missing or empty reports fail when either target is configured. Malformed policies fail validation.

Review the policy, test cases, measurement scope, and expected pass/fail results together before
adopting the release containing it. Targets are read from the selected standards release, not from
the project being checked. Changing them requires another reviewed standards release and adoption.

Existing `start_percent` records with `measured_at_commit` remain enforceable as an overall minimum.
They do not imply a changed-line target. Use either `start_percent` or `floor_percent`, not both.

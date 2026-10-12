# Per-repository exceptions

The checks read no settings from the repository they check. When one repository needs an
exception, it is recorded here, in a folder named after that repository, and reaches the check
through a pull request to this repository.

Two kinds of exception exist.

## A file exempt from a rule

`overrides/<repository>/exempt.yaml` lists paths and the rules they are exempt from, each with
a reason:

```yaml
exempt:
  - path: src/standards/rules.py
    rules: [chat-residue]
    reason: the rule examples in this file are the shapes the rule looks for
```

An entry with no reason, or naming a rule that does not exist, stops the check with an error.

## A public test fixture

A test account password that a public project publishes in its own documentation, such as a
database image's default login, may appear in source if the line says so and the fixture is
listed in `overrides/<repository>/public_fixtures.yaml` with the page it comes from:

```yaml
public_fixtures:
  - value: the-literal-as-it-appears-in-source
    published_at: https://the.page/that/publishes/it
```

A line in that repository then passes the secret-literal rule when it carries the words
"public fixture" in a comment and its literal matches an entry whose `published_at` is a URL.

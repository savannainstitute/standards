"""docs/RULES.md is what the rule list renders, and every rule renders once."""

from pathlib import Path

from standards import render_rules, rules

ROOT = Path(__file__).parents[1]


def test_rules_doc_is_current():
    rendered = render_rules.target(ROOT).read_text(encoding="utf-8")
    assert rendered == render_rules.render()


def test_every_rule_has_a_heading():
    text = render_rules.render()
    for rule in rules.RULES:
        assert f"\n## {rule.id}\n" in text
    assert text.count("\n## ") == len(rules.RULES)


def test_rule_ids_are_unique_and_kebab_case():
    ids = [rule.id for rule in rules.RULES]
    assert len(ids) == len(set(ids))
    for rule_id in ids:
        assert rule_id == rule_id.lower()
        assert " " not in rule_id
        assert "_" not in rule_id

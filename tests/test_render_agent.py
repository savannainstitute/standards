"""The agent files are what the rule list renders, in every place they sit."""

import json
import re
from pathlib import Path

import pytest

from standards import agent_files, render_agent, rules, rules_check

ROOT = Path(__file__).parents[1]
DESTINATIONS = [ROOT, *sorted((ROOT / "templates").iterdir())]


def test_agents_file_is_current():
    path = agent_files.canonical("AGENTS.md")
    assert path.read_text(encoding="utf-8") == render_agent.render_agents()


def test_hook_patterns_are_current():
    path = agent_files.canonical("rules_hook.json")
    assert path.read_text(encoding="utf-8") == render_agent.render_patterns()


def test_every_rule_is_in_the_agents_file():
    text = render_agent.render_agents()
    for rule in rules.RULES:
        assert text.count(f"\n- `{rule.id}`") == 1


def test_agents_file_ends_with_the_marker():
    text = render_agent.render_agents()
    assert text.rstrip("\n").endswith(agent_files.MARKER)
    assert text.count(agent_files.MARKER) == 1


def test_hook_patterns_match_the_check():
    """The emphasis words and the contrast shapes are the check's own."""
    data = json.loads(render_agent.render_patterns())
    assert set(data["emphasis_words"]) == rules_check.EMPHASIS_WORDS
    assert data["contrast"] == [p.pattern for p in rules_check.CONTRAST]
    assert re.compile(data["characters"]).search(chr(0x2014))


@pytest.mark.parametrize("destination", DESTINATIONS, ids=lambda p: p.name)
def test_copies_are_current(destination):
    assert agent_files.compare(destination) == []

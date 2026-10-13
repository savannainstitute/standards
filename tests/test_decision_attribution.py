"""Decisions credited to a person or a date are reported, ordinary dates not.

Each line below was written with the answer beside it before the rule
existed. The rule names no person: it reads the shape of the sentence.
"""

import pytest

from standards import rules_check


@pytest.mark.parametrize(
    "line",
    [
        "Line length is 79 (Zack, 2026-10-12).",
        "The threshold of 0.4 was approved by Kevin.",
        "Decided on 2026-09-30: outputs go under data/derived.",
        "Monika asked that the map keep county lines.",
        "Kept as a list per Scott's request.",
        "The ordinal-scale slider, per Scott 2026-08-07.",
    ],
)
def test_reported(line):
    assert rules_check.DECISION_ATTRIBUTION.search(line)


@pytest.mark.parametrize(
    "line",
    [
        "Copyright (c) 2026 Savanna Institute",
        "Inputs were fetched on 2026-10-01 from the county portal.",
        "Growth follows Brainard and Dawson (2024).",
        "## 1.1.0",
        "The model is fit per plot and per year.",
        "Each row is one tree measured in 2025.",
        "Metashape said 80.6 percent and OpenDroneMap said 28.7 percent.",
        "Sync said everything was synced.",
        "500,000 items per Shared Drive.",
        "Grantees connecting farmers to markets (per Inside Philanthropy).",
        "Approved by HazelBase on the contract that the loader reads it.",
        "One requested read owns one bounded buffer.",
    ],
)
def test_not_reported(line):
    assert not rules_check.DECISION_ATTRIBUTION.search(line)

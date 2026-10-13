"""A repository's agent files are compared up to the marker line."""

from standards import agent_files


def test_compare_names_a_changed_copy(tmp_path):
    """A copy edited above the marker is reported; below it is not."""
    agent_files.write_copies(tmp_path)
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8") + "\nThis repository's notes.\n",
        encoding="utf-8",
    )
    assert agent_files.compare(tmp_path) == []
    agents.write_text(
        "An extra line.\n" + agents.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / ".gemini" / "settings.json").unlink()
    assert agent_files.compare(tmp_path) == [
        ".gemini/settings.json",
        "AGENTS.md",
    ]


def test_write_copies_keeps_the_notes_below_the_marker(tmp_path):
    """A rewrite restores the organization's text and keeps the notes."""
    agent_files.write_copies(tmp_path)
    agents = tmp_path / "AGENTS.md"
    notes = "\nRun the pipeline with the small sample first.\n"
    agents.write_text(
        "Edited.\n" + agents.read_text(encoding="utf-8") + notes,
        encoding="utf-8",
    )
    agent_files.write_copies(tmp_path)
    text = agents.read_text(encoding="utf-8")
    assert text.endswith(agent_files.MARKER + "\n" + notes)
    assert not text.startswith("Edited.")

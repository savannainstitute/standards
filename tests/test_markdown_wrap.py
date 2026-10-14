"""Generated Markdown is filled as Prettier fills it."""

from standards import markdown_wrap


def test_a_code_span_is_never_split():
    """The span holds three spaces; it stays one word."""
    assert markdown_wrap.words("a `b c d` e") == ["a", "`b c d`", "e"]


def test_fill_breaks_before_the_word_that_passes_the_width():
    """Twenty 4-letter words and 19 spaces make 99 columns; one more wraps."""
    text = " ".join(["word"] * 21)
    first, second = markdown_wrap.fill(text).split("\n")
    assert len(first) == 99
    assert second == "word"


def test_list_items_hang_two_spaces():
    """The 2-column prefix, 24 words of 3 and 23 spaces make 97; one wraps."""
    text = " ".join(["abc"] * 25)
    first, second = markdown_wrap.fill(text, "- ", "  ").split("\n")
    assert len(first) == 97
    assert second == "  abc"

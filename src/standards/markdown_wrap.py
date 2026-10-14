"""Wrap generated Markdown the way Prettier wraps it, so the check passes it.

Prettier's prose wrap fills each paragraph to the Markdown width and never
breaks inside a code span; fill() does the same, so a file written by
render-agent or render-rules is already formatted.
"""

# Markdown printWidth in configs/prettierrc.yaml, and MD013 in markdownlint.
WIDTH = 100


def words(text):
    """Split text on spaces, keeping each code span whole."""
    found = []
    current = []
    in_code = False
    for token in text.split(" "):
        current.append(token)
        in_code ^= token.count("`") % 2 == 1
        if not in_code:
            found.append(" ".join(current))
            current = []
    if current:
        found.append(" ".join(current))
    return [word for word in found if word]


def fill(text, first="", rest=""):
    """Return text filled to WIDTH, line 1 after first and the rest after rest."""
    lines = []
    line = first
    for word in words(text):
        prefix = first if not lines else rest
        if line != prefix and len(line) + 1 + len(word) > WIDTH:
            lines.append(line)
            line = rest + word
        elif line == prefix:
            line = prefix + word
        else:
            line = f"{line} {word}"
    lines.append(line)
    return "\n".join(lines)

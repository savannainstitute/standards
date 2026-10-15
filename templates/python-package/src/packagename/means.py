"""The mean of a measurement for each plot, the package's one working pattern.

Replace this module with the package's own topics; keep its shape: a
function that refuses a missing column, a non-numeric column and a blank
value, so that no result rests on a silent guess.
"""


def plot_means(rows, value, plot):
    """Return one dict per plot with its name, count and mean of the value.

    rows is a list of dicts, one per measurement, as csv.DictReader yields
    them. A blank in the value column stops the function: whether a blank
    means missing, zero or not recorded is decided by the person, not here.
    """
    if not rows:
        return []
    absent = [name for name in (value, plot) if name not in rows[0]]
    if absent:
        raise ValueError(f"the table has no column {', '.join(absent)}")
    blank = sum(1 for row in rows if str(row[value]).strip() == "")
    if blank:
        raise ValueError(
            f"{blank} blank value(s) in {value}; decide what a blank means "
            "before taking a mean"
        )
    try:
        values = [(row[plot], float(row[value])) for row in rows]
    except ValueError as error:
        raise ValueError(f"{value} is not a numeric column") from error
    by_plot = {}
    for name, number in values:
        by_plot.setdefault(name, []).append(number)
    return [
        {"plot": name, "n": len(numbers), "mean": sum(numbers) / len(numbers)}
        for name, numbers in by_plot.items()
    ]

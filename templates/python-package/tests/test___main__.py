"""The command reads a CSV file and prints one line per plot."""

from packagename.__main__ import main


def test_prints_the_means_of_a_file(tmp_path, capsys):
    """A file with plots a (2, 4) and b (9): means 3.0 and 9.0."""
    table = tmp_path / "heights.csv"
    table.write_text("plot,height\na,2\na,4\nb,9\n", encoding="utf-8")
    assert main([str(table), "--value", "height", "--plot", "plot"]) == 0
    assert capsys.readouterr().out == "a\t2\t3.0\nb\t1\t9.0\n"

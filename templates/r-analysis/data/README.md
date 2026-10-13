# Data

For every input: where it comes from, the date it was fetched, its license, its units and its
coordinate reference system, and the command or steps that fetch it.

Inputs go in a subfolder named raw. Nothing in it is ever modified, and no script writes to
it. Everything the scripts compute from the inputs goes in a subfolder named derived, which
can be deleted and rebuilt by running the analysis again.

The first script expects one input, a table named measurements.csv in the raw subfolder with
a column `plot` naming the plot each row belongs to and a numeric column `height_m`. Replace
this paragraph with the description of your own inputs.

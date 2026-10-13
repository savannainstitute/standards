# Fixtures for the self-test

`planted_a.json` and `planted_b.json` each describe a small repository: a base tree, a head tree,
the head commit's message and the pull request text. The test builds each as a git repository,
runs the slop check over it and compares the findings with `expected_a.json` and
`expected_b.json`, which were written by hand before the check existed. Each expected entry is a
rule id, a path and a line; line 0 means the finding is about the file or the pull request
rather than one line.

The fixtures are stored as ASCII-escaped JSON so that this repository's own check does not read
the planted violations as violations of these files.

Scenario A plants one violation of every rule except fix-without-test, plus four lines that
must not be reported: a dated file under the data folder, a four-line roxygen comment, three
comment lines in a YAML file, and a silenced lint line that names its rule and reason. Scenario
A carries none of the files a repository copies from this one, so standards-copy reports each
of the eight. Scenario B is given current copies of all eight by the test and changes one
source file with no test and no explanation, which is the one case fix-without-test reports.

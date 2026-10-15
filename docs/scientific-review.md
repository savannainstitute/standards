# Scientific review record

Use this record for changes to methods, calculations, data interpretation, units, identifiers,
missing-value handling, or scientific outputs. Keep the completed record with the pull request or in
project documentation linked from it. Formatting-only changes do not require this record.

The repository owner identifies a reviewer with relevant scientific expertise. Prefer someone who
did not implement the change. If independent review is unavailable, record that limitation and
restrict the intended use accordingly; a passing automated check does not replace scientific review.

## Evidence to provide

| Field           | Required information                                                                                              |
| --------------- | ----------------------------------------------------------------------------------------------------------------- |
| Intended use    | Scientific question, users, outputs, and uses the change does not support                                         |
| Method          | Equations or algorithm in scientific terms, assumptions, and references                                           |
| Inputs          | Small reference dataset, provenance, identifiers, units, and missing-value rules                                  |
| Expected result | Independently calculated values, published reference, or validated comparator; derivation and tolerance rationale |
| Reproduction    | Exact code commit, environment, command or application steps, and output location                                 |
| Comparison      | Expected and observed values, discrepancies, and investigation                                                    |
| Sensitivity     | Relevant boundary cases, invalid inputs, and effects of uncertain inputs                                          |
| Review          | Reviewer, outcome, limitations, and unresolved questions                                                          |

The reviewer checks the method and reference result without needing to read the implementation
language. The implementer supplies executable comparisons and explains any discrepancy. Changes to
expected values or tolerances require a scientific explanation; updating an expected result merely
to make a test pass is not validation. For an application, test exported data as well as the
display.

## Worked reference case

The Python package template computes per-plot means. Use these measurements:

```csv
plot,height_cm
001,0
001,6
010,9
```

For plot `001`, two measurements sum to 6 cm, so the mean is 3 cm. For plot `010`, one measurement
gives a mean of 9 cm. Identifiers retain leading zeros. Zero is a measurement; a blank is missing.

After installing the template package, save the data as `reference.csv` and run:

```text
python -m packagename reference.csv --value height_cm --plot plot
```

The output must contain plot `001`, count 2, mean 3.0, and plot `010`, count 1, mean 9.0. A sum in
place of a mean, a changed denominator, or an incorrect unit conversion must fail the comparison.
Replacing a measurement with a blank must produce an explicit error. Choose reference cases for each
project's actual risks; this example does not validate a biological model or research app.

## Review outcome

Record one outcome: accepted for the stated use; accepted with explicitly limited use; or revision
required. Explain the evidence and limits. The owner resolves required revisions before using the
affected results. Preserve the reviewed code and inputs so the comparison can be repeated.

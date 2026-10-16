# Adoption and recovery procedure

## Before changing a project

The owner and coordinator record the current commit, workflow and hook revisions, working test
command, runtime, required data, deployment dependencies, and current deadlines. Identify the
contributor who will perform the pilot and the administrator who can recover access. Confirm that
there are no uncommitted changes before applying a release bundle.

List blocking findings separately from advisory findings. Agree on required cleanup before enabling
required checks. Identify the behavior and failure cases the project must test. Review coverage
reports and record any justified numeric targets through the central repository policy. Verify
passing and failing cases before adopting the release that enforces those targets. Do not rename a
repository, rewrite its history, change visibility, or change deployment credentials as an
incidental part of installing CI.

## Adoption and rollback

Install the selected standards package in an isolated Python environment. Install Node.js 24 with
npm for the Markdown hook. Use the full, tested standards commit with `standards-adopt`, following
the commands in the standards README. Review the workflow, local hook, and agent-file changes
together. Run `pre-commit run --all-files`, inspect any formatting edits, then rerun until clean.
Commit the bundle in a pull request and inspect hosted checks before merging.

Before merging, record the previous standards commit and how to restore the project if this is its
first adoption. For an update, apply the previous full release with the same adoption command and
rerun local and hosted checks. For first adoption, revert the adoption commit through a pull
request. Preserve unrelated project changes. Do not change a shared branch or tag to roll back one
project.

If the checks prevent normal work, keep enforcement unchanged while the update is repaired or rolled
back. An emergency bypass, if necessary, requires the owner to record the reason, scope, and
follow-up verification; it must not become the normal contribution process.

## Pilot record

| Measure             | Record                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------ |
| Setup               | Clean-machine installation steps, elapsed time, and missing prerequisites                  |
| Ordinary change     | Small representative change made by the owner or contributor                               |
| Scientific evidence | Reference case and review record where scientific behavior changes                         |
| Findings            | True defects, incorrect findings, unclear messages, and correction time                    |
| Independence        | Whether the contributor interpreted and resolved findings without coordinator intervention |
| Compute             | Runner, check duration, run count, storage, and billed usage when available                |
| Recovery            | Previous release restored and a representative change rechecked                            |
| Decision            | Ready to activate checks, revisions required, or migration deferred with reason            |

Successful template CI establishes that the mechanism works on starter projects. It does not satisfy
the owner-operated pilot. Activate enforcement only after a contributor completes the process and
the owner agrees that the remaining requirements are workable.

## Writing findings and agent support

Formatting tools can apply deterministic formatting. Spelling and prose findings require review of
the context. Keep identifiers, dataset values, quotations, reference titles, and external API names
unchanged. Use inline code for identifiers and block quotations for quoted source text. Report
incorrect findings with the rule ID and a minimal example; do not rewrite scientific meaning merely
to remove a warning. Advisory findings do not block merging.

Record the agent application and version, whether it loads project instructions, whether its hook
actually runs, and whether a planted prose issue is corrected without changing a literal. Run
pre-commit explicitly when hook support is unavailable. Gemini CLI configuration does not establish
Antigravity compatibility. Hook protocol tests do not establish that an installed agent application
loads those hooks. Verify this on the contributor's installed client during setup.

## Shared compute and administration

Review gross usage, discounts, and net charges separately; separate compute from storage. Use the
existing repository baseline and pilot duration to estimate added demand. Estimate runner minutes as
expected monthly runs multiplied by observed minutes per run, then apply the applicable billing
rates and allowances. Include retries and platform-specific jobs. Do not extrapolate normal demand
from a period in which workflows were disabled.

First use reporting and alerts without automatic individual-share shutdowns. A spending stop is a
separate decision because it can prevent required checks from completing. Before enabling it, record
the approved amount, billing administrator, backup, recipients, review frequency, and procedure for
restoring blocked work. No spending amount is established by these standards.

The administrator runs the report-only dry run and reviews its planned writes before enabling the
schedule. Assign a backup who can locate repository variables, App ownership and key rotation,
billing controls, workflow logs, and release rollback instructions. Have that person repeat a dry
run and a rollback in a test project. Documentation is not a substitute for access or this exercise.

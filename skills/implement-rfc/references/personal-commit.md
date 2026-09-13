# Personal product commits

Use this procedure before editing product files in personal mode, when finishing
their acceptance, or when a product/tracker commit was interrupted. Continue to
use the shared engineering and acceptance rules; this helper changes persistence.

## Claim and begin

Commit the eligible private claim with `issue_board.py --repo-root SOURCE claim
CARD --json`. Then, while the owned product files are clean, call:

```sh
python3 scripts/personal_commit.py --repo-root SOURCE begin --id CARD --paths path/to/file path/to/another
```

Use helper paths from the selected skill asset root. The command requires a
committed In Progress card and the bound source/tracker lane. It returns an
`operation` token and records the claim, source baseline and explicit file list
under the external runtime root. New files may be named before they exist.
Directories, pathspecs, symlinks and submodules refuse. Begin is complete when its
receipt exists; product edits may now start. Keep unrelated staged or unstaged
files outside the owned list.

## Finish

Run the required product checks. Save the shared approved acceptance decision
(`approved`, `decision`, `records`) in an external JSON file. Each record supplies
its criterion, outcome and portable evidence; the helper fills `revision` with
the actual product commit. `human-pending` parks the card with its pending records.

```sh
python3 scripts/personal_commit.py --repo-root SOURCE finish --operation TOKEN --message "Improve product behavior" --acceptance /external/acceptance.json
```

Add `--pr-text /external/proposed-pr.md` when preparing publication text. Before
creating a source branch or using separately generated publication text, run
`validate-text` with `--branch`, `--message`, or `--pr-text`. This validates only;
branch creation and publication retain their existing authority requirements.

The selected source branch, product paths/content, message and supplied PR text
must contain no known private IDs, tracked private document paths, actual
tracker/runtime paths or distinctive bookkeeping fields. Generic product prose
about RFC directories or the implement-rfc skill remains valid. Acceptance evidence
commits to the tracker with portable references, while local paths stay in the
receipt. This guard checks known private references; the author still reviews
project documentation and publication prose for disclosure.

Product content must decode strictly as UTF-8, or as UTF-16/UTF-32 with a byte-order
mark. Binary/control-bearing data and unsupported encodings refuse instead of
receiving a lossy privacy check. This applies to both prepared and adopted commits.
Neither command currently supports binary approval or a binary bypass option.

Finish captures only the named files, requires their index entries to be
unstaged, and preserves unrelated staged and unstaged edits. It refuses a changed
source baseline or claim. Active commit hooks and required signing refuse before
branch mutation because the prepared-commit adapter cannot honor those contributor
requirements. Use the normal-commit adoption path below; removing contributor
requirements is not a recovery step. The helper runs no acceptance commands itself.

Completion means both commits exist, the tracker records the actual product SHA,
the owned indexes agree with their commits, and tracker files match its committed
acceptance. `status: complete` describes this persistence operation; a parked
card still requires its recorded human decision. Tracker-only acceptance remains
available through `issue_board.py finish` without `--paths`.

## Adopt a normal contributor commit

For required hooks/signing, start with the same committed claim and `begin`
receipt before editing. Review the ordinary message and selected content through
the privacy rules above, then make the source commit separately with the project's
normal Git process, preserving explicit ownership and required hooks/signing.

The authorized integrator may execute this normal Git process directly when the
existing hook/signing setup permits. It adds no human checkpoint; an actual host
or key permission prompt remains the user's decision.

Run the required checks against that exact commit and call:

```sh
python3 scripts/personal_commit.py --repo-root SOURCE adopt --operation TOKEN --source-revision FULL_SHA --acceptance /external/acceptance.json
```

Add the proposed PR text as for finish. Adopt requires that SHA to be the current
source head, with exactly the begin baseline as its sole parent. Its nonempty
changes must stay within the owned paths; the actual committed message, paths and
file content must pass privacy validation. It creates only the tracker completion
commit and saves the actual source SHA in the receipt and acceptance. It does not
invoke or claim to verify hooks/signatures itself. A failed adoption preserves the
existing source commit and refuses tracker completion; it cannot undo disclosure
in a normal commit, so inspect private text before creating that commit.

If the normal Git process was interrupted, inspect its actual result and supply
the exact SHA explicitly. An editing receipt never guesses which ordinary commit
to adopt. After adoption prepares its receipt, use resume for tracker-side failures.

## Recover

```sh
python3 scripts/personal_commit.py --repo-root SOURCE status --operation TOKEN
python3 scripts/personal_commit.py --repo-root SOURCE resume --operation TOKEN
```

Status is observational. An `editing` receipt has no prepared commit; continue
the owned edits and call finish. Retrying finish requires the exact stored
message, acceptance and PR proposal; a changed proposal refuses. Resume uses the
durable proposal without rereading those input files.

The adapter prepares normal Git commit objects using external indexes and saves
their exact identities durably before advancing either branch with a compare-and-
swap ref update. Thus a crash after source commit but before its receipt update is
recovered by the already recorded SHA, parent and tree. Source history carries an
ordinary message and no private marker. Tracker completion uses the same protocol.
Each tree and its commit parent use one captured baseline. If a branch advances
concurrently, the guarded ref update refuses. Recovery payloads must match the
prepared tree and its parent's original bytes. Before recording completion, the
helper verifies the owned index entries and exact tracker worktree bytes against
the prepared commits; later source worktree edits remain untouched.
Receipt writes are atomic and synchronized; process-held external locks release
on exit. Git index locks remain ordinary Git locks and must be preserved while
their owner is active.

If either history differs from both its recorded parent and expected commit,
resume refuses ambiguity. Concurrent changes to an owned index entry or tracker
completion file also refuse and remain intact. Preserve successful commits and
the receipt, inspect the exact pair, and return the conflict to the integrator for
explicit reconciliation. Do not reset, create a replacement operation, or infer
completion from an attempted tracker update. Later uncommitted source edits stay
in the worktree; recovery never writes product files.

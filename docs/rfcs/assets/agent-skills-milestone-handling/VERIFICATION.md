# Verification: exercise discovery and actual decisions

## Offline implementation gates

Use the shared installed helper path through two different disposable consumer
contexts from an unrelated working directory. Resolve each consumer explicitly;
verify no shared payload mutation during read/check and no writes to the other
consumer during adoption. Reuse existing board/context fixtures and subprocess
entrypoints rather than building a second harness.

Test raw authored input before anything creates live plan links, remaps IDs or
prepares an assignment. Exercise new-plan discovery, real import mapping, current
selection, intermediate card progress, safe continuation and resume from just a
live RFC/issue reference. Preserve authored group membership even when only the
first issue in a dependency chain is initially Ready. The example raw pack in
`fixtures/raw-pack/` is intentionally tempting: individual issue headings use
"Milestone M1" and similar labels, but the canonical plan has two three-card outcomes.

Negative tests must include duplicate keys, unknown schema, duplicate IDs, cycle,
missing ref, whole/partial overlap, ambiguous criterion, escaped plan pointer,
conflicting plan candidates, drifted generated view, existing plan collision,
partial adoption/retry, narrower user scope, and incomplete required coverage.
Reference resolutions must account for live ID remapping and lane moves.

Continuation tests include falsely completed intermediate cards; completed cards
with missing public-path evidence; accepted partial-card criteria while the card
stays open; same-native-ID resume with a new dispatch; justified fresh boundary;
related next-outcome reuse; context recovery mid-milestone; active/unknown writer;
late/duplicate result; cancel; required review relay; human-pending independent
work; and affected versus unrelated plan amendment. Use actual obligation inputs,
not only a conveniently preselected disposition. A helper cannot prove semantic
coherence, but it must refuse structurally impossible completion.

## Instruction and authoring gates

Read the actual rendered role instructions used by both host fixtures. Verify the
coordinator has a mandatory plan-resolution/binding step before implementation
dispatch; engineering intake and planless formation enter the first integrator;
workers can own a complete explicitly assigned multi-card slice; and review/leaf
permissions remain unchanged. Reconcile active contradictory reset rules rather
than adding a warning beside them. Pointer existence/keyword checks are insufficient.

Compare actual common-path words/bytes including role prompts and consumer-required
material. Keep one-fix, resume, status, review, import and native-limited paths clear.
Report counts as static text, not runtime input or quota savings. Reference writing
principles are retained under `reference/writing-for-agents/`.

Plan/template/render checks run outside a consumer without its full stack. Separately
exercise runtime reconciliation with its actual stack. Both are required: author-side
validation cannot certify current repository truth, and runtime availability must
not be a prerequisite for creating a useful offline pack. Include plan examples,
schemas and authoring guidance in normal source-dump/package manifests.

## Native boundary

Follow `NATIVE_QUALIFICATION.md` only after the offline path works. Real native
courses prove discovery/selection/continuation choices. Unit tests cannot replace
them. No broad per-case agent matrix; no repeated unchanged build/review cycles.
Record missing native capability as pending, continue unrelated allowed implementation,
and leave required acceptance open. Generated adapters or banners do not prove host
loading. Existing configured routes remain unchanged for comparison and correctness.

## Acceptance evidence map

| Criteria | Direct evidence |
|---|---|
| AC01–AC03 | Raw structured/legacy discovery, schema/ref checks, imported ID map, live linkage, resume and no-op/collision public CLI cases |
| AC04–AC05 | Bound assignment + intermediate card + complete integration + explicit continue/fresh decisions; ownership/stale/duplicate cases |
| AC06–AC08 | Planless, partial, single RFC, subset, large issue, dependency chain, amendment and interrupted recovery tests |
| AC09 | Actual rendered instructions and assignments, focused verification/review behavior, common-path reading measurements |
| AC10 | End-to-end helper entrypoints through two linked disposable consumers and explicit negative cases |
| AC11 | Both bounded actual interactive-driver courses with precise identity/outcome evidence |
| AC12 | Selected safe adoption receipt, unchanged routes/addenda, direct final acceptance and truthful limitations |

The RFC's stable full criterion IDs belong in the live closeout. Pack-provided
`fixtures/scenarios.json` describes inputs and expected properties, not performed
checks. See VALIDATION.md only for artifact checks actually run during authoring.

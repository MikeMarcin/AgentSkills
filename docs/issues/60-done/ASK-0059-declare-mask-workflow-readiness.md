---
schema: "implement-rfc.card.v1"
id: "ASK-0059"
title: "Declare MASK workflow readiness for implement-rfc"
status: "Done"
rfcs: ["RFC-ASK-0011"]
depends_on: []
closeout_for: ["RFC-ASK-0011"]
metadata: {"mandate": "mask-corrective-ux-readiness D10 rev3", "upstream": "ManageAgentSkills MASK-0090 / RFC-MASK-0019"}
acceptance: [{"criterion":"RFC-ASK-0011-AC01","outcome":"pass","revision":"4bd053c","evidence":{"kind":"observation","detail":"MASK parsed the shipped descriptor (16 roles, one action); first ensure reported workflow incomplete with all roles setup_required and no code run."}},{"criterion":"RFC-ASK-0011-AC02","outcome":"pass","revision":"4bd053c","evidence":{"kind":"observation","detail":"Approved --allow-setup run published 16 roles and the portable lock; ensure ok with workflow complete; unchanged rerun no-op."}},{"criterion":"RFC-ASK-0011-AC03","outcome":"pass","revision":"0f8b3cd","evidence":{"kind":"observation","detail":"--check never ran code; interactive decline exit 4 with nothing staged; entrypoint refuses changed/appeared inputs and unknown action/role/parameters."}},{"criterion":"RFC-ASK-0011-AC04","outcome":"pass","revision":"4bd053c","evidence":{"kind":"observation","detail":"Deployed bytes equal generate_roles output; addenda confined to their consumer; fresh clone with lock complete; changed package input made the lock stale."}},{"criterion":"RFC-ASK-0011-AC05","outcome":"pass","revision":"4bd053c","evidence":{"kind":"observation","detail":"unrequire then ensure applied native_role.remove for all MASK-owned roles; tampered role reported modified, never overwritten."}},{"criterion":"RFC-ASK-0011-AC06","outcome":"pass","revision":"0f8b3cd","evidence":{"kind":"observation","detail":"Preflight ready/incomplete on real consumers; unsupported against an old-program stub returning link-only success."}},{"criterion":"RFC-ASK-0011-AC07","outcome":"pass","revision":"0f8b3cd","evidence":{"kind":"observation","detail":"Structure gate 0 violations; focused tests 8/8 and 19/19; full suite 420/421 with one pre-existing routing expectation failure; portable manifest regenerated."}}]
---

# ASK-0059: Declare MASK workflow readiness for implement-rfc

Governing RFC: [RFC-ASK-0011](../../rfcs/RFC-ASK-0011-declared-mask-workflow-readiness.md).

## Objective and owned paths

Ship `mask-workflow.json`, the staged preparation entrypoint and the startup
preflight for implement-rfc; prove them with MASK's real CLI against disposable
consumers; record the handoff facts MASK-0090 needs.

Owned paths:

- `skills/implement-rfc/mask-workflow.json`
- `skills/implement-rfc/scripts/prepare_mask_roles.py`
- `skills/implement-rfc/scripts/workflow_preflight.py`
- `skills/implement-rfc/scripts/render_runtime_adapters.py` (shared generation function only)
- `skills/implement-rfc/tests/test_mask_workflow.py`
- `skills/implement-rfc/generated/portable-manifest.json`
- `skills/implement-rfc/README.md`, `skills/implement-rfc/SKILL.md` (readiness paragraph)
- this card and the RFC

## Acceptance

Criterion coverage: RFC-ASK-0011-AC01 through RFC-ASK-0011-AC07.

## Closeout

RFC_BASE_SHA: 0dd8a29a3d93776a22da325db4d9a4f3299daf2a

Planned cards: ASK-0059 (sole card and closeout). Implementation commits: 4bd053c
(descriptor, staging entrypoint, preflight, `generate_roles` refactor) and 0f8b3cd
(docs, focused tests, portable manifest). The completion commit is the finish
commit of this card.

Handoff facts for ManageAgentSkills MASK-0090: card `ASK-0059`; descriptor
`skills/implement-rfc/mask-workflow.json` (sha256
`9575dc4fa8a69900236bd8d68634fdca5759124d91acf3cf8c22c6e83e4d70f1`); setup action
`prepare-roles`, entrypoint `skills/implement-rfc/scripts/prepare_mask_roles.py`;
preflight `skills/implement-rfc/scripts/workflow_preflight.py`; required roles
rfc-integrator, rfc-utility, rfc-scout, rfc-test-runner, rfc-reviewer, rfc-worker,
rfc-worker-deep, rfc-reviewer-critical for both codex and claude; consumer inputs
`project-config`, `project-rules` (required) and `execution-selection` (optional);
MASK `skill validate` fingerprint at 0f8b3cd
`sha256:7ff27a61692d396346221f8d14e7f0618a39618f446be8df01cc26b215ebc116`.

Evidence was produced on macOS (Darwin 25.6.0, Python 3.14.7) by running
ManageAgentSkills `mask.py` (working tree, program version 0.2.0, `capabilities`
readiness `workflow_readiness_v1`) as a subprocess with a private `MASK_HOME` and
`HOME`, against a Git clone of this repository as the source and two disposable
consumers (`alpha`, `beta`) with distinct `role_addenda`. No real host profile or
MASK state was modified; one early preflight probe ran `ensure --check`
read-only against the real program state and reported `integration.approval_required`.

| Criterion | Direct evidence / outcome | Implementation revisions |
|---|---|---|
| RFC-ASK-0011-AC01 | Pass: first `ensure` on alpha reported `workflow=incomplete`, `workflow.incomplete` exit 4, all 16 roles `setup_required`, links committed, no code ran; MASK's descriptor parser accepted the file (16 roles, one action). | 4bd053c |
| RFC-ASK-0011-AC02 | Pass: `ensure --expect-plan-hash --allow-setup legacy/implement-rfc:prepare-roles` ran the entrypoint from the frozen snapshot, published 16 role files and `native-roles.lock.json`, returned ok with `scope_readiness.workflow=complete`; unchanged rerun: ok, `changed=false`, no setup proposal. | 4bd053c |
| RFC-ASK-0011-AC03 | Pass: `--check` with consent flags reported `not_run`; interactive `n` on beta returned exit 4 with "declined; nothing ran", no roles, no stage; unit tests show the entrypoint exits 2 without staging when an input changed or an absent optional input appeared, or the action/role/parameters are unknown. | 4bd053c, 0f8b3cd |
| RFC-ASK-0011-AC04 | Pass: deployed alpha bytes equal `generate_roles` output for alpha (16/16, lock hashes match); `ALPHA-ONLY` addendum appears only in rfc-worker; beta shows `BETA-ONLY` only in rfc-reviewer and zero `ALPHA-ONLY` occurrences; a fresh clone of beta with checked-in roles and lock is `complete` with `repository-owned` roles and no setup proposal; updating the source (SKILL.md is a declared package input) made the lock stale (`readiness.drift`, `setup_required`) until re-approved. | 4bd053c |
| RFC-ASK-0011-AC05 | Pass: `project unrequire implement-rfc` then `ensure` applied `native_role.remove` for all MASK-owned role files on alpha, leaving the repository-owned lock; a tampered role on beta was reported `modified` (exit 4) and never overwritten. | 4bd053c |
| RFC-ASK-0011-AC06 | Pass: preflight returned `ready` on both consumers after setup, `incomplete` with the `modified` blocker after tampering, and `unsupported` against a stub program without `workflow_readiness_v1` that returned link-only success (unit test). | 4bd053c, 0f8b3cd |
| RFC-ASK-0011-AC07 | Pass: `python scripts/verify_documentation.py --root .` 11 RFCs, 59 cards, 0 violations; focused `test_mask_workflow.py` 8/8 and `test_render_runtime_adapters.py` 19/19; full skill suite 420/421 with 4 skips; the one failure (`test_standard_worker_target`) predates this work (owner Fable 5.1 amendment at 0af7c0e, tests explicitly not rerun then); portable manifest regenerated and `validate_portable_agents.py --source-only` valid. | 0f8b3cd |

## Integration judgment and limitations

Closeout review runtime: none; local touched-code review only (small surface
whose outputs MASK independently validates). Native Windows and Linux lanes were
not exercised. Host loading of deployed roles in a fresh Codex/Claude host was
not verified; MASK reports `host_load=not_verified` and the preflight passes that
through. The staged setup runs package code with user permissions; it is not a
sandbox. The standalone renderer remains a distinct owner of its own outputs and
was not migrated; the lock is repository-owned and intentionally survives
retirement. Disposable fixture roots, the private MASK_HOME and the source clone
were removed after evidence collection. No push, publication, credential or
permission change occurred, and the ManageAgentSkills checkout was only read
and executed, never edited.

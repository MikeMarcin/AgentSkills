---
schema: implement-rfc.card.v1
id: ASK-0103
title: Preserve enforcement for existing project-prefixed station v2 bindings
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"command","detail":"Exact canonical and former-marker guard/lifecycle enforcement passed source tests; unknown bound markers, identity/branch/authority/lease and lifecycle negatives remained refused."}},{"criterion":"AC2","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"observation","detail":"Actual EXAMPLE-HOST PreToolUse admitted distinct host turns REDACTED-SESSION-007 and REDACTED-SESSION-008 at unchanged stn-39ef5ffb/generation0/endpoint and held PID55408 lease. 168 installed source blobs and helper digest matched the committed candidate. Source FF and native probe tools executed; no restart or manual state seed. Receipts: native-admission-sync-receipt.json and native-initial-probe/receipt.json. Actual takeover/retirement protections passed focused station-control cases."}},{"criterion":"AC3","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"command","detail":"Guard/parser 56/56 and focused control 4/4 passed on final shared candidate; original compatibility control 31/31 evidence remains relevant. Portable-source, documentation and diff checks passed."}},{"criterion":"AC4","outcome":"pass","revision":"4c0f70c490445780dd8bb5805481d0da326a4bf3","evidence":{"kind":"observation","detail":"Scoped MASK transaction committed with three actions at the approved original authoring root; both project links measured. Actual EXAMPLE-HOST PreToolUse admitted distinct host turns REDACTED-SESSION-007 and REDACTED-SESSION-008 at unchanged stn-39ef5ffb/generation0/endpoint and held PID55408 lease. 168 installed source blobs and helper digest matched the committed candidate. Source FF and native probe tools executed; no restart or manual state seed. Receipts: native-admission-sync-receipt.json and native-initial-probe/receipt.json."}}]
---

# Preserve enforcement for existing project-prefixed station v2 bindings

Unblock ordinary authorized turns through a current bound station whose consumer
launcher retains the former project-prefixed v2 schema marker. Continued work at
the same endpoint is not a takeover and needs no supervisor stop per iteration.

## Current failure

AITO's newly launched `EXAMPLE-WINDOWS-STATION` writes
`aito.implement-rfc.remote-station.v2`, while the shared guard expects
`implement-rfc.remote-station.v2` and returns inactive. Shared lifecycle identity
also rejects the former marker. The exact current Codex endpoint, main branch,
lane-commit authority and owning supervisor lease are present. Calling that held
lease a conflicting old writer incorrectly turns ordinary station continuation
into a physical Ctrl+C/relaunch prerequisite.

Observed binding: station `stn-39ef5ffb`, task
`REDACTED-SESSION-006`, checkout `C:\code\git\aito` on EXAMPLE-HOST.
Existing AITO helper source emits the prefixed marker; this is a source contract
mismatch rather than an old Windows installation. Native desktop control through
this exact task is proven separately and does not certify station authority.

## Owned scope

Shared guard/lifecycle compatibility and their focused tests, with directly
relevant guidance and generator-owned manifest upkeep. Preserve canonical new
output, existing identity/history and every authority, checkout, lease and turn
check. AITO consumer launcher corrections and scoped MASK deployment are separate
authorized readiness work for the coordinator's active ENT-0058 milestone.

## Acceptance

- AC1: The precisely supported former marker receives the same complete
  identity/schema/branch/envelope/authority/lease enforcement as canonical v2.
  Unknown or unrelated markers do not become authorized through broad matching.
- AC2: Ordinary continuation through the already registered endpoint requires
  no takeover or supervisor restart. Actual ownership transfers retain their
  stop/retirement protections; a held expected station lease is not a conflict.
- AC3: Focused tests exercise canonical and supported former bindings, foreign
  identity/authority/branch, missing lease and real transfer protection. Relevant
  portable-source/documentation gates and diff hygiene pass.
- AC4: A scoped MASK-managed Windows deployment is actually observed by the
  current task, and successive correctly guarded station turns execute without
  physical intervention or identity reset. Record revision, binding and results;
  fixtures alone do not prove the live readiness repair.

No sidecar-PID kills, direct registry normalization, MASK internal edits,
unrequested publication, extra user-facing chat or fabricated native acceptance.

## Implementation checkpoint — 2026-10-04

The shared lifecycle and guard accept only canonical v2 and the exact former
AITO-prefixed v2 marker under the existing identity, endpoint, branch, lease and
turn checks. An unknown marker carrying a Codex binding now refuses tools rather
than disabling enforcement. The JSON schema records the same precise read
compatibility. New launcher output remains canonical. Station-control guidance
distinguishes same-endpoint continuation from an actual ownership transfer.

Focused tests first reproduced legacy guard inactivity, lifecycle refusal and
failed successive guarded turns. After correction, the final checks passed:

```sh
/Users/EXAMPLE/Documents/Personal/aito/.venv/bin/python -W error::ResourceWarning -m unittest discover -s skills/implement-rfc/tests -p test_remote_station_guard.py -v
/Users/EXAMPLE/Documents/Personal/aito/.venv/bin/python -W error::ResourceWarning -m unittest discover -s skills/implement-rfc/tests -p test_station_control.py -v
python3 -B skills/implement-rfc/scripts/render_runtime_adapters.py --write-source-manifest
python3 -B skills/implement-rfc/scripts/validate_portable_agents.py --source-only
python3 -B scripts/verify_documentation.py --root .
git diff --check
```

Guard: 27/27; station control: 31/31. JSON-schema cases ran with `jsonschema`
available. Tests exercise both markers, two turns under the same held supervisor,
wrong endpoint/branch/authority, missing lease, malformed/unknown markers,
existing lifecycle identity and transfer/retirement protection. No fixture
registry or lifecycle bytes change during read/turn compatibility checks.

The named manifest generator also corrected pre-existing CRLF digests: unchanged
source bytes match their LF Git blobs; old recorded hashes match the CRLF
conversion of those blobs. No unrelated source file was changed. The source
and documentation gates passed with 15 RFCs, 103 cards and no violations.

AC4 remains pending: the coordinator will deploy the committed candidate through
a scoped MASK dev-link with exact source bytes, then collect actual successive
guarded turns at the current Windows endpoint. No source push or live registry
edit is authorized here. The unrelated `.mask.lock.json` change is preserved.

## Actual native closeout — 2026-10-04

The scoped MASK transaction committed all three actions through the approved
`C:\code\git\AgentSkills` authoring root, and both consumer links were measured.
After ASK-0104 resolved the actual Codex tool-output admission contract, the
current task executed two distinct actual PreToolUse-admitted turns on shared
candidate `4c0f70c490445780dd8bb5805481d0da326a4bf3`:
`REDACTED-SESSION-007` (source synchronization) and
`REDACTED-SESSION-008` (native build probe). The first turn's
authorization was cleared before the second. Station `stn-39ef5ffb`, endpoint
`REDACTED-SESSION-006`, generation 0, lane-commit authority,
lease PID 55408 and supervisor PID 7836 remained unchanged. No restart, physical
intervention or manually seeded admission occurred.

The actual task audited 168 package blobs and the exact helper/guard hashes.
Six metadata-only Git flags remain on Windows with zero content diffs; this is
not called a clean authoring checkout. Receipts are retained in AITO's
`code/.build/runs/implement-rfc/unattended-20261003-windows/ent0058/` as
`native-admission-sync-receipt.json` and `native-initial-probe/receipt.json`,
with station-before/after logs. The committed MASK receipt is retained at the
run root as `windows-completed-mask-and-public-status.txt`.

AC1–AC4 pass. The second turn exposed independent native product defects
(`/O2` versus `/RTC1`, and project Natvis emitted as ClInclude); ENT-0058 remains
open for those repairs and stopped-target acceptance. Unrelated builders and
the existing containers.sln session were preserved; no global writer-quiescence
claim is made. Unrelated `.mask.lock.json` is preserved and no source push occurred.

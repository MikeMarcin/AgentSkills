---
schema: implement-rfc.card.v1
id: ASK-0103
title: Preserve enforcement for existing project-prefixed station v2 bindings
status: "In Progress"
rfcs: []
depends_on: []
---

# Preserve enforcement for existing project-prefixed station v2 bindings

Unblock ordinary authorized turns through a current bound station whose consumer
launcher retains the former project-prefixed v2 schema marker. Continued work at
the same endpoint is not a takeover and needs no supervisor stop per iteration.

## Current failure

AITO's newly launched `aito-main-win` writes
`aito.implement-rfc.remote-station.v2`, while the shared guard expects
`implement-rfc.remote-station.v2` and returns inactive. Shared lifecycle identity
also rejects the former marker. The exact current Codex endpoint, main branch,
lane-commit authority and owning supervisor lease are present. Calling that held
lease a conflicting old writer incorrectly turns ordinary station continuation
into a physical Ctrl+C/relaunch prerequisite.

Observed binding: station `stn-39ef5ffb`, task
`01a10525-e3fa-7250-85cf-c27f2f84897d`, checkout `C:\code\git\aito` on JaegAW.
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
/Users/jaeger/Documents/Personal/aito/.venv/bin/python -W error::ResourceWarning -m unittest discover -s skills/implement-rfc/tests -p test_remote_station_guard.py -v
/Users/jaeger/Documents/Personal/aito/.venv/bin/python -W error::ResourceWarning -m unittest discover -s skills/implement-rfc/tests -p test_station_control.py -v
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

---
schema: implement-rfc.card.v1
id: ASK-0106
title: Recover pending takeover before acquiring a fresh station lease
status: "Done"
rfcs: []
depends_on: []
acceptance: [{"criterion":"AC1","evidence":{"kind":"command","detail":"Launcher checks and composed interrupted-transfer fixture verify recovery before lease, endpoint retirement, identity mismatch and refusal without stop proof."},"outcome":"pass","revision":"70d04b19d79b9fc82e8fd233923266c4fa5dafa2"},{"criterion":"AC2","evidence":{"kind":"command","detail":"Focused retry tests refresh negative supervisor proof and preserve transfer identity; free leases leave runtime proof null. Durable interrupted-transfer tests pass."},"outcome":"pass","revision":"70d04b19d79b9fc82e8fd233923266c4fa5dafa2"},{"criterion":"AC3","evidence":{"kind":"command","detail":"WSL launcher 68 and takeover 51 tests pass. Windows launcher 68 pass; initial takeover harness recursion corrected and all three new regressions pass. Existing checks pass, one POSIX test skipped on Windows. Portable validation, manifest and documentation gate pass."},"outcome":"pass","revision":"70d04b19d79b9fc82e8fd233923266c4fa5dafa2"},{"criterion":"AC4","evidence":{"kind":"observation","detail":"With owner stop confirmation, actual WSL public takeover cleared pending state; public --fresh reached Codex ready and Claude Connected. Status: managed generation4, pending null, intended station supervisor lease held. Installed payload remains 4bdf12d; source deployment not claimed."},"outcome":"pass","revision":"70d04b19d79b9fc82e8fd233923266c4fa5dafa2"}]
---

# Recover pending takeover before acquiring a fresh station lease

Owner mandate, 2026-10-13: fix BetterPullReview on JaegAW refusing
`python3 scripts/launch_remote_station.py --fresh` with
`finish pending local takeover before relaunch`. The previous ASK-0105/BPR-1401
hook removal explicitly retained that pending takeover.

Baseline: `4bdf12d49f0572e23d5d877b9655d977a4381ee0`.
Execution: direct primary, no delegated agents. Unrelated admission helper/schema
edits are outside this slice. Scope: shared launcher, takeover and supervisor
stop recovery, focused tests and directly relevant station instructions. Repair
the named WSL consumer through supported management; no publication or push.

- AC1: An explicit fresh launch retries a pending takeover before obtaining its
  new supervisor lease. Ordinary launches and unproven stops remain refused,
  with the public recovery command and original obligations preserved.
- AC2: A negative supervisor observation is retried; positive runtime proof
  survives an interrupted takeover. A free lease or absent proxy never
  certifies a stopped runtime.
- AC3: Launcher/takeover/lease regression tests pass on Windows and WSL using
  disposable fixtures; the source manifest and documentation gate agree.
- AC4: The actual JaegAW pending takeover is completed after the owner's real
  stop confirmation, and the public fresh-launch path is exercised. Record
  the installed payload and any remaining runtime limitation explicitly.

## Verification and native repair

Selected recipe: direct primary; no agents or engineering model calls. Preflight
reported `project.not_registered` for this canonical source checkout; deterministic
helper work used its explicit repository context, without installing roles or
claiming host loading. No authored milestone plan governs this standalone repair.

The owner confirmed the old station work is stopped in this chat. The existing
installed helper's supported takeover returned local generation 3, pending null
and a free lease. Then the actual public command
`python3 scripts/launch_remote_station.py --fresh` created Codex task
`01a138d2-16eb-7cd0-807e-a7b1997dbf07` and Claude session
`session_012HztGHeTyv6qKQn4KKwrxx`, which reached Connected. Subsequent public
status reports managed generation 4, pending null and its held supervisor lease.
The launcher session is intentionally running for the owner's remote station;
there are no remaining task-owned test writers.

Installed WSL payload remains commit `4bdf12d49f0572e23d5d877b9655d977a4381ee0`,
digest `8268ee8acf816959e141313c21c4d106d4507c41c788c05c02e2c7f9539bd509`.
This native result proves repair and successful startup with that installed
version, not loading of the new source patch. MASK authoring-link previews
refused `import.authoring_required` and `source.alias_conflict` because the
existing approved tap has no authoring checkout. No links, catalog, locks or
MASK internal state were altered. Source publication/push and a normal reviewed
upgrade remain outside this no-publication slice.

Focused results:

- WSL: `python3 -B -m unittest discover -s skills/implement-rfc/tests -p
  test_launch_remote_station.py`: 68/68 pass. Same command selecting
  `test_station_control.py`: 51/51 pass, including real POSIX group-stop fixtures.
- Windows: launcher 68/68 pass. The initial run exposed a pre-existing local
  remote path-separator fixture failure; the fixture now uses `Path.as_posix()`.
  Initial takeover suite: 51 cases, one skipped POSIX case and one new test
  harness recursion error. Corrected harness to pass real Git commands through;
  all three new takeover regressions then pass in a focused rerun. Earlier
  passing existing checks retain unchanged inputs.
- Both hosts: portable source valid. Source manifest regenerated. Documentation:
  15 RFCs, 106 cards, zero violations. `git diff --check` passes.
- Self-review: recovery precedes lease acquisition, identity mismatch and
  unproven runtime stops refuse before launch, durable transfer ID/history and
  retired endpoints survive recovery. Full fresh-context replacement is required;
  confirmation stays in the outer recovery process. A negative supervisor
  observation is retried, while a free lease never becomes runtime proof.

Continuation: bounded source and native repair complete. Any future publication
must use explicit owner authorization, then upgrade only the named consumer and
verify installed bytes. Unrelated admission-helper/schema edits remain untouched.

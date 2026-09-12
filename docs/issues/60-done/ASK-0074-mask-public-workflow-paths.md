---
schema: "implement-rfc.card.v1"
id: "ASK-0074"
title: "Consume MASK-owned workflow paths without hardcoded lock locations"
status: "Done"
rfcs: ["RFC-ASK-0011"]
depends_on: []
acceptance: [{"criterion":"AC1","outcome":"pass","revision":"df308c56d6d55a91fd5ae5f1df9ee5aa0ca69212","evidence":{"kind":"observation","detail":"22 renderer tests passed with advertised future paths, canonical-first retired fallback, unsupported and unsafe capability refusal; real MASK capabilities used for disposable beta renderer --check."}},{"criterion":"AC2","outcome":"pass","revision":"df308c56d6d55a91fd5ae5f1df9ee5aa0ca69212","evidence":{"kind":"observation","detail":"Compared 16 roles in each of AgentSkills and ManageAgentSkills contexts against 266c364: generated fingerprint differs, other bytes equal. Correctly withheld compatibility assertion and documented one-time setup."}},{"criterion":"AC3","outcome":"pass","revision":"df308c56d6d55a91fd5ae5f1df9ee5aa0ca69212","evidence":{"kind":"observation","detail":"22 renderer tests, 8 MASK entrypoint/preflight tests, portable source validator pass; real MASK qualifier 44/44 steps on native macOS with two disposable consumers."}}]
---

# ASK-0074

September 12, 2026 owner-authorized direct deployment follow-up paired with
ManageAgentSkills MASK-0097. Baseline `266c364c140fd0412556265ee43df31a7811cf70`;
preserve existing renderer, README and test edits relocating the lock.

AC1: standalone renderer reads lock paths from MASK capabilities, retaining
canonical-first fallback and refusing unsupported MASK instead of guessing paths.
AC2: compare native output bytes in two consumer contexts; declare prior lock
hash pairs only if exact output equivalence holds, otherwise record why setup
remains required without weakening role hashes.
AC3: focused renderer/staging tests and portable source validation pass.

Scope: canonical renderer/helper, descriptor, focused tests, README and portable
manifest. No native role/routing changes, live consumer migration or push.

## Verification and handoff

Source implementation: `df308c56d6d55a91fd5ae5f1df9ee5aa0ca69212`.
MASK counterpart: `973eede8fb9b4d1289fc684deac15b3e6c0fdb13`.
On native macOS, 22 renderer tests and 8 MASK entrypoint/preflight tests pass;
`validate_portable_agents.py --source-only` passes with regenerated manifest.
Renderer tests supply future canonical/retired locations from a fake capability
response, verify fallback precedence and refuse malformed or unsupported paths.
The real MASK qualifier passed 44/44 subprocess steps with two disposable
consumers and a fresh clone. Its source was this commit; MASK was the unchanged
working candidate subsequently committed as the counterpart revision above.
The disposable beta renderer also passed `--check` using the real counterpart's
capabilities via `MASK_PROGRAM`.

Output comparison with baseline renderer `266c364` in AgentSkills and
ManageAgentSkills contexts found 16/16 roles per consumer differ only in the
generated fingerprint. The generator hashes its whole source into each role's
marker, including for path-only changes. Therefore no `compatible_locks` pair
was added: the output-equivalence assertion would be false. The runtime feature
is qualified in MASK with an actually output-identical fixture helper edit.
This one-time adoption needs setup; future MASK-only lock moves no longer edit
package inputs. Existing active consumers were not regenerated or cleaned.

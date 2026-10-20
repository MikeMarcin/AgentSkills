# Audio questions source acceptance

Assignment: one integrated `audio-feedback` milestone, source-only AgentSkills on
main; run `audio-2026-10-19`, segment `implementation-1`, mandate `audio-source-v1`,
child `/root/audio_questions`. The owner selected per-clip answers with sequential
A/B comparison and no implicit sibling rejection. No migration, deployment, real
profile changes or Faraday review mutation was authorized or performed.

RFC_BASE_SHA is `7cc31bbd61c08c8445afd52df9fed8997b7069ab`. Source candidate:
`2eff4c355c470cce9a629b488abb0d0e487fec19`. Source changes are confined to
`skills/attended-review/`; live RFC/card/plan/evidence records support that change.
The immutable original draft remains unchanged.

## Acceptance evidence

| Criterion | Actual check and result | Source revision |
|---|---|---|
| AC01 | Generated mixed example and public init/prepare/serve through a source symlink in two distinct disposable consumer roots; distinct sessions. Root native browser showed ordinary brief, six independent audio questions and decode control with purpose/scope. Pass. | `2eff4c3` |
| AC02 | Root browser A/B switching started B at zero, restored A feedback and left siblings pending; Death C rejection remained independent. Public mixed partial intake also leaves other clips unanswered. Pass. | `2eff4c3` |
| AC03 | Actual live browser playback advanced while feedback saved and focus stayed in the note; loop/replay/timestamp/comparison and failed-decode control behaved as specified. Real standalone page code also executes its offline controls, keyed media retention and diagnostics in the deterministic DOM/media model. Pass for source behavior; native file-URL audio playback remains unverified. | `2eff4c3` |
| AC04 | Public tests and actual browser navigation/reload/host restart preserved unanswered feedback without an answer. Offline-page execution exported an unanswered comment, and public CLI import/retry persisted it without a verdict. Death C note preserved “reject for death; consider for pain” as separate intent. Pass. | `2eff4c3` |
| AC05 | Actual browser revised Death C feedback while retaining rejection, then withdrew answer while retaining feedback. Durable submitted history corroborates both. Host-down editing visibly failed, retained newer local text, and exported it; import changed only that feedback and retry was a no-op. Tests cover optimistic conflicts and stale refresh/orphan draft retention. Pass. | `2eff4c3` |
| AC06 | Public CLI/HTTP tests validate a mixed partial set atomically, retain histories and idempotent operation IDs, refuse stale clip/purpose/fingerprint and unprepared intake. Golden legacy fingerprint captured from RFC_BASE_SHA matches; version-1 imports work. Offline-page-generated version-2 packet roundtrips through public CLI. Pass. | `2eff4c3` |
| AC07 | Browser handback stopped playback and reported one answered/seven pending/three pending with feedback. Durable event sequence 39 and all eight protections agree. Public handback-only waiter stays blocked through feedback and diagnostics and returns on handback. No new wait/model loop. Pass. | `2eff4c3` |
| AC08 | Canonical skill, format contract and portable example agree on versioning, answer revision/withdrawal, 20 MiB intake, four images/4 MiB data-URL bounds and offline/stdlib runtime. Focused suite, deterministic page execution, portable-source validation and documentation gate pass. Pass. | `2eff4c3` |

Commands and output/revision receipts: [focused tests](focused-tests.json),
[portable source](portable-source.json), [documentation](documentation.json).
Browser observations and screenshots: [browser evidence](browser-evidence.md).
The source runtime has no new dependency; Node is used only by deterministic page
tests and is not required to run a session.

## Durable fixture corroboration

Consumer-a session `a496eafa027fe444753902472e445a2f` reached sequence 39. Its
handed-back event names `death-C` as decided; `brief`, `broken`, `death-A`, `death-B`,
`launcher-A`, `launcher-B`, `launcher-C` remain pending. `feedback_pending` is
`brief`, `launcher-A`, `launcher-B`. All eight remained protected after handback.
Death C submitted history retains its original rejection/reuse wording and revised
wording. One decode diagnostic remains attached to the unanswered broken candidate.

While the first host was stopped, durable Launcher B still contained the earlier
saved text. The exported newer local draft was imported through the public CLI;
only Launcher B feedback changed. Re-import accepted nothing and sequence remained
38. A normal host restart on a new ephemeral origin then displayed that newer text.
This is export/import recovery across origins, not automatic retry across origins.
Consumer-b session `0e54f8888d4c65c3d9c71c60d42232be` is a separate fixture context.

## Scope and limits

The source criteria above use direct live browser evidence plus offline code
execution/transport checks. The browser security policy refused `file://`; no
alternate browser or HTTP file-serving bypass was attempted. Native local-file
playback and native Windows host qualification remain unperformed. This is not a
Faraday audition, rights determination, in-game acceptance or consumer deployment.
No human creative-acceptance ceremony is required by this RFC.

Self-review used writing-for-agents and code-simplifier instructions. It removed
duplicate answer-history snapshots, made save/status handling explicit, preserved
legacy offline cache and verdict retries, and guarded newer drafts against stale
status. No independent review was required or claimed. Test failures during
construction were missing methods in the minimal test DOM (URLSearchParams and
classList); those fixture omissions were fixed. The final tests exercise the real
page code and do not certify native file-browser behavior.

Final committed-candidate browser smoke on consumer-b also passed: time advanced 0.244098→3.308371 seconds during autosave, player stayed unpaused, note focus/text remained, A/B/A feedback restored, and partial export contained zero decisions plus exactly one saved comment. The host was then stopped cleanly.

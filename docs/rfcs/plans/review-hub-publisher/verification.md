# RFC-ASK-0018 verification

Milestone `session-publication` (plan `review-hub-publisher`), cards ASK-0129 and
closeout ASK-0130. RFC_BASE_SHA `ff6b40727e673cf4defd9a6cbaca7816558eb1de`.
Implementation commits: `156b32ba80218133a6998735dde68d992f71d8ea` (publisher,
tests, contract and README) and `3cb685646a09f454fd407a5596c036683db261a2` (init
publication-point assertion). **Integrated wire-contract revision:
`3cb685646a09f454fd407a5596c036683db261a2`**, contract text in
[session-contract.md, Optional hub publication](../../../../skills/attended-review/references/session-contract.md#optional-hub-publication).

All checks use disposable roots, the existing fake Tailscale CLI and in-process
HTTPS fixture hubs whose certificates are issued per run by a throwaway fixture CA
(`openssl`). `ATTENDED_REVIEW_HUB_FIXTURE_CONNECT` routes TCP to loopback while
TLS still verifies `hub.example.ts.net`. No real network, Tailscale settings, hub
or installed consumer was touched.

| Criterion | Check | Outcome | Commit |
|---|---|---|---|
| AC01 | `test_never_enabled_session_gains_no_files_fields_output_or_network`: serve/browser/CLI with a listening fixture hub, no files beyond `session.json`, no `hub` field, unchanged hosting keys, zero requests, environment alone enables nothing. [ac01_differential.py](ac01_differential.py) ([evidence](ac01-differential.json)): same command sequence (init, prepare, loopback serve, import, observe, pause, start, hand-back, failing ready, status, conflicts, resume-development, stop) through the RFC_BASE_SHA helper and the candidate gives identical exit codes, stdout, stderr, files and session bytes after normalizing IDs, tokens, ports, PIDs and times. | pass | 3cb6856 |
| AC02 | `test_exact_wire_contract_at_publication_points_without_private_material`: exact 11 keys and count keys, `PUT /api/sessions/{id}`, JSON, no Origin/Authorization; records at host start, CLI prepare (including failed preparation), browser answer, pause, start, hand-back, stop, later observe and init; loopback-served session publishes nothing; titles, content, criteria, checkout path, loopback URL, remote URL/credentials and revision strings absent; remote basename only; harness not relabelled. | pass | 3cb6856 |
| AC03 | `test_slow_unreachable_and_broken_metadata_preserve_review_behaviour`: with a 6 s hub, 15 browser intakes each answer in under 1.5 s and all save; attempts never overlap (arrivals more than 2.8 s apart) and coalesce (at most 2 + elapsed/3); deadline warning appears; stop within 6 s; no-host CLI attempt bounded, unchanged output, failing command keeps exit 1/stderr; unreachable warning then cleared on recovery; `hub.json` replaced by a directory leaves commands and status unaffected with no request. | pass | 3cb6856 |
| AC04 | `test_invalid_origins_certificates_and_redirects_never_leak_the_capability`: 10 invalid origins (scheme, userinfo, path, query, fragment, non-ts.net, IP, port, trailing dot, empty) by flag and environment exit 1 before any file or request; an impostor certificate gets no request ("certificate verification failed"); a 307 is refused, not followed; diagnostics contain no token or payload. | pass | 3cb6856 |
| AC05 | `test_heartbeat_resends_the_identical_snapshot_without_advancing_order`: with the fixture heartbeat override the hub receives identical records (same revision and sequence) at the interval; constants are 300 s heartbeat and 3 s deadline, so a real hub hears from a live host within 5 minutes plus the deadline. | pass | 3cb6856 |
| AC06 | `test_disjoint_counts_states_and_ordering_across_restart_and_concurrency`: mixed ready/slow-unprepared/answered/feedback-only/withdrawn candidates give the defined disjoint counts; paused, partial handed-back (ready 2), restart of review, resume-development to preparing; stop and restart keep the review sequence while revisions increase and the URL rotates; 6 concurrent CLI callers produce strictly increasing sequences by revision, one body per revision, ending at the final sequence. | pass | 3cb6856 |
| AC07 | `test_configuration_precedence_reuse_attachment_and_disabling`: `--hub` beats the environment; both flags exit 2; attaching with `--hub` redirects the running host; CLI from a shell without the variable reuses the saved destination; `--no-hub` beats the environment, clears the destination and cancels publication (no further requests through stop); a later environment-only serve re-enables with a larger revision and later commands reuse it. Browser responses never wait on the network (AC03). `test_symlinked_skill_in_two_consumers_publishes_independent_sessions` runs the symlinked skill from two consumers with independent sessions and metadata. | pass | 3cb6856 |

Suite: `python3 -B -m unittest discover -s skills/attended-review/tests` — 52 tests
OK ([evidence](focused-tests.json); 44 pre-existing unchanged). Structure gate:
`python3 -B scripts/verify_documentation.py --root .` — 18 RFCs, 130 cards, 0
violations ([evidence](documentation.json)). The new hub module ran more than 20 times during
development, including 3 concurrent runs; one early failure came from two racy test
assertions (last-overall instead of last-matching record; a server-side
concurrency counter that counted handlers still sleeping after the client's
deadline). Both were corrected before the recorded runs.

[fixture-records.json](fixture-records.json) holds actual records from a fixture
flow (start, CLI answer, partial handback, stop) for the service repository, with
capability tokens redacted and the machine name normalized.

Not established here, by design: a real hub, NAS deployment, real tailnet TLS,
native Windows publication (the fake-Tailscale fixture is POSIX-only, as for the
existing transport tests), and harness detection for Codex beyond its documented
environment variables. Closeout review runtime: local implementer self-review
(claude-opus-5-5); no independent or human review is required by the RFC.

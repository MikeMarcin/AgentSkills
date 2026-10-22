# Tailscale prototype continuation

Assignment `/root/tailscale_phone_closeout`; mandate `tailscale-prototype-v1`;
run `tailscale-prototype-2026-10-21`, segment `phone-closeout-1`; AgentSkills main.
Plan `attended-review-tailscale`, milestone `private-transport`, ASK-0118 TS01–TS03.
No delegated agents. Original source `b42654b`; evidence follow-up `32d2694`.
Final source candidate `f52a273e4058ae58f420c19bc2d2370fe857610d`, following bounded
cleanup commits `7cfacd7` and `ba14c79`. Baseline remains `3ef1d0f0f44192d13311c1bac0d904cb19741a7a`.

The phone receipt was reconciled by the coordinator through consumed cursor 12:
saved note, explicit ACCEPT on the prepared phone-note fingerprint, handback, and
one remaining pending item. The verdict applies only to disposable transport intake
at `b42654b`; no product acceptance or phone reload inference. Private receipt:
`/tmp/attended-review-tailscale-prototype/phone-handback-status.json`. Private session
identity and URL remain in the coordinator's demo-continuation JSON beside it.
The coordinator stopped that host and removed its fixture after recording intake.

The native cleanup error is corrected. A macOS shell launcher without exec meant
single-PID shutdown did not reliably signal its real Serve child. The final code
owns a separate POSIX process group, sends SIGINT for Serve's Ctrl+C cleanup, keeps
the three-second kill fallback and polls only the exact session with an eight-second
monotonic deadline. Failed time-window-only and single-PID-interrupt attempts remain
in live-attempt.json; no precise daemon expiry cause is claimed.

Verification: seven focused public transport tests pass at `f52a273`, including
interrupt-required shell launcher, delayed mapping disappearance, genuine lingering
failure, two linked consumers and request boundaries. Fresh native macOS stop passes
at that candidate: helper exit 0 in 0.238s, Serve {}, shell launcher and native child
absent, fixture removed. Existing 39-test/page evidence remains historical and relevant
to unchanged behavior; client code was not changed. Documentation, scoped board,
checkpoint and diff checks are recorded for the final closeout.

Owned changed source paths: skills/attended-review/scripts/attended_review.py,
tests/test_attended_review.py, tests/fixtures/fake_tailscale.py and
references/tailscale-serve.md. Upkeep is limited to this plan/evidence directory and
the existing ASK-0118 card. The terminal board helper refused reopening Done, so
historical acceptance and status were preserved and post-review evidence appended.
No new card/RFC, MASK state, setup, permission, credential, Funnel, deployment,
publication or push changes. Unrelated .mask.lock.json remains dirty and unstaged.

Ownership/commands: quiescent after closeout. All owned test/native commands completed;
no server, waiter, protected disposable candidate or repository writer is handed off.
Private raw receipts retained; temporary native test fixtures removed. No repository
writers besides this bounded owner were used. The coordinator owns final user reporting.

Next action: report that phone save, verdict and handback worked and cleanup is now
verified. No required obligation remains in this bounded prototype. Phone browser
reload, automatic agent wake and native Windows lifetime remain unverified; forced
parent death and friendly shared mounts retain their documented limits. Preserve
qualified waiter/manual-resume behavior. Further feature work needs a new assignment.

## Later instruction-policy follow-up

`remote-review-standard-v1`, assignment `/root/remote_review_standard`, consumes
subsequent successful phone-to-Codex automatic continuation at source `38d0715`
(helper runtime `f52a273`). Its sanitized evidence is appended to
[verification.md](verification.md#subsequent-awake-codex-handback-qualification)
and the reusable runtime qualification lives in Driver waiting. The earlier
automatic-wake limitation above remains historical; matching short awake Codex
continuation is now observed. The current instruction milestone's
[continuation](../remote-review-standard/continuation.md) owns its source checks
and final candidate. No live session/process or acceptance decision is handed off.
